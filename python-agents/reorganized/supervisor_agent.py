import logging
from typing import Dict, Any, List, Optional, AsyncIterator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import StructuredTool
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointTuple
import redis
import json
import asyncio
from datetime import datetime
import orjson

from config import Config
from models import AgentState
from agents.guide_agent import get_guide_agent, GuideAgent
from agents.order_agent import get_order_agent, OrderAgent
from agents.payment_agent import get_payment_agent, PaymentAgent
from models import ChatRequest

logger = logging.getLogger(__name__)

# --- 自定义 Redis Checkpointer 实现 (保持不变) ---
class RedisCheckpointer(BaseCheckpointSaver):
    def __init__(self, redis_url: str):
        try:
            self.redis = redis.Redis.from_url(redis_url)
            self.redis.ping()
            logger.info(f"✅ RedisCheckpointer: 成功连接到 Redis 服务器: {redis_url}")
        except redis.ConnectionError as e:
            logger.error(f"❌ RedisCheckpointer: 无法连接到 Redis 服务器: {redis_url}. 错误详情: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ RedisCheckpointer: 初始化失败: {e}")
            raise

    async def aget_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        key = f"langgraph:checkpoint:{thread_id}"
        try:
            data = await asyncio.to_thread(self.redis.get, key)
            if data:
                checkpoint_data = orjson.loads(data)
                checkpoint = checkpoint_data.get("checkpoint")
                metadata = checkpoint_data.get("metadata", {})
                parent_ts = checkpoint_data.get("parent_ts")
                if checkpoint:
                    return CheckpointTuple(
                        config=config,
                        checkpoint=checkpoint,
                        metadata=metadata,
                        parent_ts=parent_ts
                    )
            return None
        except Exception as e:
            logger.error(f"RedisCheckpointer: 获取检查点失败 for {thread_id}: {e}")
            return None

    async def aput_tuple(self, config: Dict[str, Any], checkpoint: Checkpoint, metadata: Dict[str, Any],
                         parent_ts: Optional[str]) -> str:
        thread_id = config["configurable"]["thread_id"]
        key = f"langgraph:checkpoint:{thread_id}"
        try:
            def serialize_message(msg):
                if isinstance(msg, BaseMessage):
                    return {"type": msg.type, "content": msg.content}
                return msg
            serialized_checkpoint = orjson.loads(orjson.dumps(checkpoint, default=serialize_message))
            data_to_store = {
                "checkpoint": serialized_checkpoint,
                "metadata": metadata,
                "parent_ts": parent_ts,
                "timestamp": datetime.now().isoformat()
            }
            await asyncio.to_thread(self.redis.set, key, orjson.dumps(data_to_store), ex=3600)
            return data_to_store["timestamp"]
        except Exception as e:
            logger.error(f"RedisCheckpointer: 保存检查点失败 for {thread_id}: {e}")
            raise

    async def alist(self, config: Dict[str, Any]) -> AsyncIterator[CheckpointTuple]:
        thread_id_prefix = "langgraph:checkpoint:"
        try:
            keys = await asyncio.to_thread(self.redis.keys, f"{thread_id_prefix}*")
            for key in keys:
                thread_id = key.decode('utf-8').replace(thread_id_prefix, '')
                tuple_data = await self.aget_tuple({"configurable": {"thread_id": thread_id}})
                if tuple_data:
                    yield tuple_data
        except Exception as e:
            logger.error(f"RedisCheckpointer: 列出检查点失败: {e}")


# --- 1. 定义监管者 Agent 的工具 ---
class SupervisorTools:
    def __init__(self, guide_agent: GuideAgent, order_agent: OrderAgent, payment_agent: PaymentAgent):
        self.guide_agent = guide_agent
        self.order_agent = order_agent
        self.payment_agent = payment_agent

    def get_tools(self):
        # 定义异步包装函数
        async def _guide_agent_process_message_wrapper(user_input: str, session_id: str) -> str:
            return await self.guide_agent.process_message(user_input=user_input, session_id=session_id)

        async def _order_agent_process_message_wrapper(user_input: str, session_id: str) -> str:
            return await self.order_agent.process_message(user_input=user_input, session_id=session_id)

        async def _payment_agent_process_message_wrapper(user_input: str, session_id: str) -> str:
            return await self.payment_agent.process_message(user_input=user_input, session_id=session_id)

        return [
            StructuredTool.from_function(
                name="guide_agent_process_message",
                # 【关键修正】直接传递 async def 函数
                func=_guide_agent_process_message_wrapper,
                args_schema=ChatRequest,
                description="""当用户需要商品推荐、商品信息查询、产品对比等购物辅助信息时使用。
                                输入参数: 一个包含 'user_input' (str) 和 'session_id' (str) 的 JSON 对象。
                                返回商品推荐报告或相关购物信息。"""
            ),
            StructuredTool.from_function(
                name="order_agent_process_message",
                # 【关键修正】直接传递 async def 函数
                func=_order_agent_process_message_wrapper,
                args_schema=ChatRequest,
                description="""当用户需要查询订单状态、物流信息、创建订单、修改订单、取消订单、申请退款等订单相关操作时使用。
                                输入参数: 一个包含 'user_input' (str) 和 'session_id' (str) 的 JSON 对象。
                                返回订单处理结果或相关订单信息。"""
            ),
            StructuredTool.from_function(
                name="payment_agent_process_message",
                # 【关键修正】直接传递 async def 函数
                func=_payment_agent_process_message_wrapper,
                args_schema=ChatRequest,
                description="""当用户需要进行支付、查询支付状态、处理退款（支付层面）等支付相关操作时使用。
                                输入参数: 一个包含 'user_input' (str) 和 'session_id' (str) 的 JSON 对象。
                                返回支付处理结果或相关支付信息。"""
            ),
        ]

# --- 2. 定义监管者 Agent ---
class SupervisorAgent:
    def __init__(self, guide_agent: GuideAgent, order_agent: OrderAgent, payment_agent: PaymentAgent):
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL_NAME,
            temperature=Config.LLM_TEMPERATURE,
            api_key=Config.SILICONFLOW_API_KEY,
            base_url=Config.SILICONFLOW_API_BASE
        )
        self.supervisor_tools = SupervisorTools(guide_agent, order_agent, payment_agent).get_tools()

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个高级智能助手，负责根据用户请求将任务路由给合适的子代理。
                        子代理包括：
                        - guide_agent_process_message: 处理商品推荐、购物辅助等。
                        - order_agent_process_message: 处理订单查询、创建、修改、取消等。
                        - payment_agent_process_message: 处理支付、退款、支付状态查询等。

                        当决定调用子代理时，你必须严格按照以下格式生成工具调用：
                        {{
                          "tool_calls": [
                            {{
                              "name": "子代理工具名",
                              "args": {{
                                "user_input": "用户原始输入内容",
                                "session_id": "{session_id}"
                              }}
                            }}
                          ]
                        }}
                        请确保 'args' 字段是一个JSON对象，并且 'user_input' 和 'session_id' 字段是必填的。
                        如果无法判断意图或没有合适的子代理，请直接回答用户。
                        """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        self.supervisor_memory = ConversationBufferWindowMemory(
            chat_memory=RedisChatMessageHistory(
                session_id="supervisor_global_history",
                url=Config.REDIS_URL
            ),
            memory_key="chat_history",
            return_messages=True,
            k=5
        )

        self.agent_executor_instance = AgentExecutor(
            agent=create_tool_calling_agent(
                llm=self.llm,
                tools=self.supervisor_tools,
                prompt=self.prompt
            ),
            tools=self.supervisor_tools,
            verbose=True,
            memory=self.supervisor_memory
        )
        print("SupervisorAgent initialized.")

    async def route_user_request(self, state: AgentState) -> Dict[str, Any]:
        user_input = state["user_input"]
        session_id = state["session_id"]

        state["chat_history"].append(HumanMessage(content=user_input))

        try:
            # 【关键修正】同时传递 'input' 和 'session_id' 给 ainvoke 的 inputs 字典
            response = await self.agent_executor_instance.ainvoke(
                {
                    "input": user_input,
                    "session_id": session_id, # 确保 session_id 存在于 inputs 字典中
                },
                config={"configurable": {"thread_id": session_id}}
            )

            if "tool_calls" in response and response["tool_calls"]:
                tool_call = response["tool_calls"][0]
                tool_name = tool_call["name"]
                raw_tool_args = tool_call["args"]

                logger.debug(f"原始工具参数: {type(raw_tool_args)} - {raw_tool_args}")

                extracted_user_input = None
                extracted_session_id = None

                # 【此处的解析逻辑保持不变，因为它处理的是LLM生成的tool_calls.args，而不是ainvoke的输入】
                # 检查 LLM 是否错误地将整个 tool_calls 结构嵌套在 args 中
                if isinstance(raw_tool_args, dict) and "tool_calls" in raw_tool_args:
                    nested_tool_calls = raw_tool_args["tool_calls"]
                    if nested_tool_calls and isinstance(nested_tool_calls, list) and len(nested_tool_calls) > 0 and isinstance(nested_tool_calls[0], dict) and "args" in nested_tool_calls[0]:
                        # 提取真正的 args 字典
                        true_args = nested_tool_calls[0]["args"]
                        extracted_user_input = true_args.get("user_input")
                        extracted_session_id = true_args.get("session_id")
                elif isinstance(raw_tool_args, dict):
                    # 如果 raw_tool_args 是一个字典，且不包含 'tool_calls'，则直接从中提取
                    extracted_user_input = raw_tool_args.get("user_input")
                    extracted_session_id = raw_tool_args.get("session_id")
                elif isinstance(raw_tool_args, str):
                    # 尝试解析字符串格式的参数 (JSON 或键值对)
                    try:
                        parsed_args = json.loads(raw_tool_args)
                        extracted_user_input = parsed_args.get("user_input")
                        extracted_session_id = parsed_args.get("session_id")
                    except json.JSONDecodeError:
                        # 尝试解析键值对格式
                        params = {}
                        for pair in raw_tool_args.split():
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                params[key.strip()] = value.strip()
                        extracted_user_input = params.get("user_input")
                        extracted_session_id = params.get("session_id")
                else:
                    raise ValueError(f"LLM 返回的工具参数类型未知或格式不正确: {type(raw_tool_args).__name__} - {raw_tool_args}")

                # 验证提取到的参数
                if not extracted_user_input or not extracted_session_id:
                    raise ValueError(f"从 LLM 返回的工具参数中未能提取到 user_input 或 session_id。原始 args: {raw_tool_args}")

                tool_args_dict = {
                    "user_input": extracted_user_input,
                    "session_id": extracted_session_id
                }

                # 验证必要参数 (这部分逻辑保持不变，但现在是基于 tool_args_dict)
                REQUIRED_PARAMS = ["user_input", "session_id"]
                if not all(key in tool_args_dict and tool_args_dict[key] is not None for key in REQUIRED_PARAMS):
                    raise ValueError(f"缺少必要参数或参数值为None: {tool_args_dict}")

                state["next_agent"] = tool_name
                state["user_input"] = tool_args_dict.get("user_input", user_input)
                state["session_id"] = tool_args_dict.get("session_id", session_id)

                state["chat_history"].append(AIMessage(content=f"已将请求路由至 {tool_name.replace('_process_message', '')}。"))

                return state
            elif "output" in response:
                logger.info(f"SupervisorAgent 直接回答: {response['output']}")
                state["agent_response"] = response["output"]
                state["next_agent"] = "FINISH"
                state["chat_history"].append(AIMessage(content=state["agent_response"]))
                return state
            else:
                logger.error(f"SupervisorAgent 返回未知响应格式: {response}")
                state["agent_response"] = "抱歉，监管者未能理解您的请求或发生未知错误。"
                state["next_agent"] = "FINISH"
                state["chat_history"].append(AIMessage(content=state["agent_response"]))
                return state

        except Exception as e:
            logger.error(f"监管者 Agent 路由失败: {e}")
            state["agent_response"] = f"抱歉，监管者在处理您的请求时发生错误: {e}"
            state["next_agent"] = "FINISH"
            state["chat_history"].append(AIMessage(content=state["agent_response"]))
            return state

# --- 3. LangGraph 工作流定义 (保持不变，因为 _wrap_agent_call 已经正确) ---
class MultiAgentWorkflow:
    def __init__(self):
        self.guide_agent = None
        self.order_agent = None
        self.payment_agent = None
        self.supervisor_agent = None
        self.workflow = None

    async def initialize_agents(self):
        self.guide_agent = await get_guide_agent()
        self.order_agent = await get_order_agent()
        self.payment_agent = await get_payment_agent()
        self.supervisor_agent = SupervisorAgent(self.guide_agent, self.order_agent, self.payment_agent)
        logger.info("所有 Agent 初始化完成。")

    def build_workflow(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("supervisor", self.supervisor_agent.route_user_request)
        workflow.add_node("guide_agent_node",
                          self._wrap_agent_call(self.guide_agent.process_message, "guide_agent_output"))
        workflow.add_node("order_agent_node",
                          self._wrap_agent_call(self.order_agent.process_message, "order_agent_output"))
        workflow.add_node("payment_agent_node",
                          self._wrap_agent_call(self.payment_agent.process_message, "payment_agent_output"))

        workflow.set_entry_point("supervisor")

        def route_to_agent(state: AgentState):
            next_agent = state.get("next_agent")
            if next_agent == "guide_agent_process_message":
                return "guide_agent_node"
            elif next_agent == "order_agent_process_message":
                return "order_agent_node"
            elif next_agent == "payment_agent_process_message":
                return "payment_agent_node"
            else:
                return END

        workflow.add_conditional_edges(
            "supervisor",
            route_to_agent,
            {
                "guide_agent_node": "guide_agent_node",
                "order_agent_node": "order_agent_node",
                "payment_agent_node": "payment_agent_node",
                END: END
            }
        )

        workflow.add_edge("guide_agent_node", END)
        workflow.add_edge("order_agent_node", END)
        workflow.add_edge("payment_agent_node", END)

        self.workflow = workflow.compile(
            checkpointer=RedisCheckpointer(redis_url=Config.REDIS_URL)
        )
        logger.info("LangGraph 工作流构建完成。")

    async def invoke_workflow(self, user_input: str, session_id: str) -> str:
        if not self.workflow:
            await self.initialize_agents()
            self.build_workflow()

        initial_state = AgentState(
            user_input=user_input,
            session_id=session_id,
            chat_history=[], # 初始为空，由监管者节点添加用户输入
            agent_response=None,
            next_agent=None,
            guide_agent_output=None,
            order_agent_output=None,
            payment_agent_output=None,
        )

        try:
            final_state = await self.workflow.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": session_id}}
            )

            if final_state.get("agent_response"):
                return final_state["agent_response"]

            if final_state.get("next_agent") == "guide_agent_process_message":
                return final_state.get("guide_agent_output", "GuideAgent 未返回有效响应。")
            elif final_state.get("next_agent") == "order_agent_process_message":
                return final_state.get("order_agent_output", "OrderAgent 未返回有效响应。")
            elif final_state.get("next_agent") == "payment_agent_process_message":
                return final_state.get("payment_agent_output", "PaymentAgent 未返回有效响应。")
            else:
                # 如果流程结束但没有明确的子 Agent 输出，可能是因为流程异常结束
                # 此时可以返回 chat_history 中的最后一条消息，或者一个通用错误
                if final_state["chat_history"]:
                    last_message = final_state["chat_history"][-1]
                    if isinstance(last_message, AIMessage):
                        return last_message.content
                return "抱歉，未能处理您的请求，请稍后再试或换个方式提问。"

        except Exception as e:
            logger.error(f"LangGraph 工作流执行失败: {e}")
            return f"抱歉，系统在处理您的请求时发生错误: {e}"

    def _wrap_agent_call(self, agent_method, output_key: str):
        async def wrapped_call(state: AgentState) -> AgentState:
            user_input = state["user_input"]
            session_id = state["session_id"]

            try:
                result = await agent_method(user_input, session_id)
                state[output_key] = result
                # 【优化】将子 Agent 的回复也添加到 LangGraph 的 chat_history
                state["chat_history"].append(AIMessage(content=result))
                return state
            except Exception as e:
                logger.error(f"子 Agent 调用失败 ({agent_method.__name__}): {e}")
                state["agent_response"] = f"抱歉，{agent_method.__name__} 在处理您的请求时发生错误: {e}"
                state["next_agent"] = "FINISH"
                # 【优化】将子 Agent 的错误回复添加到 LangGraph 的 chat_history
                state["chat_history"].append(AIMessage(content=state["agent_response"]))
                return state

        return wrapped_call


# 全局工作流实例
multi_agent_workflow_instance: Optional[MultiAgentWorkflow] = None


async def get_multi_agent_workflow() -> MultiAgentWorkflow:
    global multi_agent_workflow_instance
    if multi_agent_workflow_instance is None:
        multi_agent_workflow_instance = MultiAgentWorkflow()
        await multi_agent_workflow_instance.initialize_agents()
        multi_agent_workflow_instance.build_workflow()
    return multi_agent_workflow_instance
