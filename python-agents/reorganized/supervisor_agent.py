# supervisor_agent.py

import logging
from typing import Dict, Any, List, Optional, AsyncIterator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
# 【重要】确保这里导入的是 StructuredTool，而不是 Tool
from langchain_core.tools import StructuredTool # 【修正】导入 StructuredTool
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, \
    CheckpointTuple
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
from models import ChatRequest # 确保 ChatRequest 被导入

logger = logging.getLogger(__name__)

# --- 自定义 Redis Checkpointer 实现 (保持不变) ---
class RedisCheckpointer(BaseCheckpointSaver):
    # ... (这部分代码保持不变) ...
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
        # ... (这部分代码保持不变) ...
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
        # ... (这部分代码保持不变) ...
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
        # ... (这部分代码保持不变) ...
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
        return [
            # 商品推荐 Agent 工具
            StructuredTool.from_function( # 【修正】使用 StructuredTool.from_function
                name="guide_agent_process_message",
                func=lambda **kwargs: asyncio.run( # 【修正】func 接收 **kwargs
                    self.guide_agent.process_message(
                        kwargs.get('user_input'), # 使用 .get() 确保健壮性
                        kwargs.get('session_id')
                    )
                ),
                args_schema=ChatRequest, # 保持 args_schema 不变
                description="""当用户需要商品推荐、商品信息查询、产品对比等购物辅助信息时使用。
                                输入参数: 一个包含 'user_input' (str) 和 'session_id' (str) 的 JSON 对象。
                                返回商品推荐报告或相关购物信息。"""
            ),
            # 订单管理 Agent 工具
            StructuredTool.from_function( # 【修正】使用 StructuredTool.from_function
                name="order_agent_process_message",
                func=lambda **kwargs: asyncio.run( # 【修正】func 接收 **kwargs
                    self.order_agent.process_message(
                        kwargs.get('user_input'),
                        kwargs.get('session_id')
                    )
                ),
                args_schema=ChatRequest, # 保持 args_schema 不变
                description="""当用户需要查询订单状态、物流信息、创建订单、修改订单、取消订单、申请退款等订单相关操作时使用。
                                输入参数: 一个包含 'user_input' (str) 和 'session_id' (str) 的 JSON 对象。
                                返回订单处理结果或相关订单信息。"""
            ),
            # 支付管理 Agent 工具
            StructuredTool.from_function( # 【修正】使用 StructuredTool.from_function
                name="payment_agent_process_message",
                func=lambda **kwargs: asyncio.run( # 【修正】func 接收 **kwargs
                    self.payment_agent.process_message(
                        kwargs.get('user_input'),
                        kwargs.get('session_id')
                    )
                ),
                args_schema=ChatRequest, # 保持 args_schema 不变
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
                        "session_id": "当前会话ID"
                      }}
                    }}
                  ]
                }}
                请确保 'args' 字段是一个JSON对象，并且 'user_input' 和 'session_id' 字段是必填的。
                如果无法判断意图或没有合适的子代理，请直接回答用户。
                """),
            MessagesPlaceholder(variable_name="chat_history"),  # 监管者 Agent 自己的记忆
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        self.agent_executor = create_tool_calling_agent(
            llm=self.llm,
            tools=self.supervisor_tools,
            prompt=self.prompt
        )
        print("SupervisorAgent initialized.")

    async def route_user_request(self, state: AgentState) -> Dict[str, Any]:
        """
        监管者 Agent 的核心路由逻辑。
        它会调用 LLM 来决定将请求路由到哪个子 Agent。
        """
        user_input = state["user_input"]
        session_id = state["session_id"]
        chat_history = state["chat_history"]  # 获取监管者 Agent 自己的对话历史

        # 创建一个临时的 AgentExecutor 来执行路由决策
        # 注意：这里没有使用记忆，因为 LangGraph 会在状态中传递 chat_history
        # 并且我们希望 LLM 每次都基于最新的完整状态进行决策
        temp_executor = AgentExecutor(
            agent=self.agent_executor,
            tools=self.supervisor_tools,
            verbose=True,  # 开启 verbose 可以看到监管者 Agent 的思考过程
            # memory=ConversationBufferWindowMemory(
            #     chat_memory=RedisChatMessageHistory(session_id=f"supervisor_{session_id}", url=Config.REDIS_URL),
            #     memory_key="chat_history",
            #     return_messages=True,
            #     k=5
            # ) # 如果监管者也需要长期记忆，可以这样配置
        )

        try:
            # 调用监管者 Agent 进行决策
            # 传入完整的 chat_history
            response = await temp_executor.ainvoke({
                "input": user_input,
                "chat_history": chat_history  # 传入监管者自己的历史
            })

            # 监管者 Agent 的输出可能是直接回答，也可能是工具调用
            if "output" in response:
                # 如果是直接回答，说明监管者认为不需要转发给子 Agent
                logger.info(f"SupervisorAgent 直接回答: {response['output']}")
                # 更新状态，将监管者的直接回答放入 agent_response，并结束流程
                state["agent_response"] = response["output"]
                state["next_agent"] = "FINISH"
                return state
            elif "tool_calls" in response:
                tool_call = response["tool_calls"][0]
                tool_name = tool_call["name"]
                raw_tool_args = tool_call["args"]  # 获取原始的 args 字段

                logger.debug(f"原始工具参数: {type(raw_tool_args)} - {raw_tool_args}")  # 增强日志

                tool_args_dict = {}
                try:
                    if isinstance(raw_tool_args, dict):
                        # 已经是字典格式，直接使用
                        tool_args_dict = raw_tool_args
                    elif isinstance(raw_tool_args, str):
                        # 尝试解析字符串格式的参数
                        if raw_tool_args.startswith("{") and raw_tool_args.endswith("}"):
                            # 1. JSON字符串格式
                            tool_args_dict = json.loads(raw_tool_args)
                        else:
                            # 2. 键值对字符串格式: 'user_input=... session_id=...'
                            params = {}
                            for pair in raw_tool_args.split():  # 假设参数之间用空格分隔
                                if '=' in pair:
                                    key, value = pair.split('=', 1)
                                    params[key.strip()] = value.strip()
                            tool_args_dict = params
                    else:
                        raise ValueError(f"LLM 返回的工具参数类型未知: {type(raw_tool_args).__name__}")

                    # 验证必要参数
                    REQUIRED_PARAMS = ["user_input", "session_id"]
                    if not all(key in tool_args_dict and tool_args_dict[key] is not None for key in REQUIRED_PARAMS):
                        raise ValueError(f"缺少必要参数或参数值为None: {tool_args_dict}")

                except Exception as e:
                    logger.error(f"监管者 Agent 参数解析失败: {raw_tool_args} - 错误: {e}")
                    state["agent_response"] = "系统内部错误：无法解析您的请求参数。请尝试更清晰地表达，或稍后再试。"
                    state["next_agent"] = "FINISH"
                    return state

                # 使用解析后的参数
                state["next_agent"] = tool_name
                state["user_input"] = tool_args_dict["user_input"]
                state["session_id"] = tool_args_dict["session_id"]

                return state

        except Exception as e:
            logger.error(f"监管者 Agent 路由失败: {e}")
            state["agent_response"] = f"抱歉，监管者在处理您的请求时发生错误: {e}"
            state["next_agent"] = "FINISH"
            return state


# --- 3. LangGraph 工作流定义 ---
class MultiAgentWorkflow:
    def __init__(self):
        self.guide_agent = None
        self.order_agent = None
        self.payment_agent = None
        self.supervisor_agent = None
        self.workflow = None

    async def initialize_agents(self):
        """异步初始化所有子 Agent 和监管者 Agent"""
        self.guide_agent = await get_guide_agent()
        self.order_agent = await get_order_agent()
        self.payment_agent = await get_payment_agent()
        self.supervisor_agent = SupervisorAgent(self.guide_agent, self.order_agent, self.payment_agent)
        logger.info("所有 Agent 初始化完成。")

    def build_workflow(self):
        """构建 LangGraph 工作流"""
        workflow = StateGraph(AgentState)

        # 添加节点：每个子 Agent 作为一个节点
        workflow.add_node("supervisor", self.supervisor_agent.route_user_request)
        # 子 Agent 节点直接调用其 process_message 方法
        # 注意：这里需要确保 process_message 返回的是一个字符串，或者更新 AgentState
        # 如果 process_message 只是返回字符串，那么需要一个包装函数来更新 state
        workflow.add_node("guide_agent_node",
                          self._wrap_agent_call(self.guide_agent.process_message, "guide_agent_output"))
        workflow.add_node("order_agent_node",
                          self._wrap_agent_call(self.order_agent.process_message, "order_agent_output"))
        workflow.add_node("payment_agent_node",
                          self._wrap_agent_call(self.payment_agent.process_message, "payment_agent_output"))

        # 设置入口点
        workflow.set_entry_point("supervisor")

        # 定义条件路由：根据 supervisor 的决策路由到不同的子 Agent
        def route_to_agent(state: AgentState):
            next_agent = state.get("next_agent")
            if next_agent == "guide_agent_process_message":
                return "guide_agent_node"
            elif next_agent == "order_agent_process_message":
                return "order_agent_node"
            elif next_agent == "payment_agent_process_message":
                return "payment_agent_node"
            else:  # 如果 supervisor 决定直接回答或发生错误，则结束
                return END

        # 添加边：从 supervisor 节点到各个子 Agent 节点
        workflow.add_conditional_edges(
            "supervisor",
            route_to_agent,
            {
                "guide_agent_node": "guide_agent_node",
                "order_agent_node": "order_agent_node",
                "payment_agent_node": "payment_agent_node",
                END: END  # 如果 next_agent 是 FINISH，则直接结束
            }
        )

        # 添加边：从子 Agent 节点到 END (表示子 Agent 处理完毕，返回结果)
        workflow.add_edge("guide_agent_node", END)
        workflow.add_edge("order_agent_node", END)
        workflow.add_edge("payment_agent_node", END)

        # 编译工作流
        self.workflow = workflow.compile(
            checkpointer=RedisCheckpointer(redis_url=Config.REDIS_URL)  # 使用自定义的 RedisCheckpointer
        )
        logger.info("LangGraph 工作流构建完成。")

    async def invoke_workflow(self, user_input: str, session_id: str) -> str:
        """
        调用 LangGraph 工作流处理用户请求。
        """
        if not self.workflow:
            await self.initialize_agents()
            self.build_workflow()

        # 初始状态
        # LangGraph 的 RedisCheckpointer 会自动从 checkpointer 加载历史
        # 我们只需要提供 config={"configurable": {"thread_id": session_id}}
        initial_state = AgentState(
            user_input=user_input,
            session_id=session_id,
            chat_history=[],  # 监管者 Agent 自己的历史，由 checkpointer 填充
            agent_response=None,  # 监管者直接回答的响应
            next_agent=None,  # 监管者路由到的下一个 Agent
            # 子 Agent 的输出字段，用于从 state 中提取最终结果
            guide_agent_output=None,
            order_agent_output=None,
            payment_agent_output=None,
        )

        try:
            # 调用工作流
            # config 中的 configurable.thread_id 用于 LangGraph 的检查点（记忆）
            final_state = await self.workflow.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": session_id}}
            )

            # 从最终状态中提取响应
            # 优先返回监管者直接回答的响应
            if final_state.get("agent_response"):
                return final_state["agent_response"]

            # 否则，根据哪个子 Agent 被调用，从对应的 output 字段获取结果
            # 注意：这里需要根据你的 _wrap_agent_call 函数的实现来获取
            if final_state.get("next_agent") == "guide_agent_process_message":
                return final_state.get("guide_agent_output", "GuideAgent 未返回有效响应。")
            elif final_state.get("next_agent") == "order_agent_process_message":
                return final_state.get("order_agent_output", "OrderAgent 未返回有效响应。")
            elif final_state.get("next_agent") == "payment_agent_process_message":
                return final_state.get("payment_agent_output", "PaymentAgent 未返回有效响应。")
            else:
                # 如果流程结束但没有明确的子 Agent 输出，可能是因为流程异常结束
                return "抱歉，未能处理您的请求，请稍后再试或换个方式提问。"

        except Exception as e:
            logger.error(f"LangGraph 工作流执行失败: {e}")
            return f"抱歉，系统在处理您的请求时发生错误: {e}"

    def _wrap_agent_call(self, agent_method, output_key: str):
        """
        包装子 Agent 的 process_message 方法，使其能够更新 AgentState。
        节点函数直接修改并返回 AgentState 对象。
        """

        async def wrapped_call(state: AgentState) -> AgentState: # 【修正】返回类型改为 AgentState
            user_input = state["user_input"]
            session_id = state["session_id"]

            try:
                # 调用子 Agent 的方法
                result = await agent_method(user_input, session_id)
                # 直接修改 state 对象
                setattr(state, output_key, result) # 【修正】直接修改 AgentState 对象的属性
                # 确保返回更新后的状态
                return state # 【修正】返回修改后的 AgentState 对象
            except Exception as e:
                logger.error(f"子 Agent 调用失败 ({agent_method.__name__}): {e}")
                # 如果发生错误，直接修改 state 对象
                state.agent_response = f"抱歉，{agent_method.__name__} 在处理您的请求时发生错误: {e}"
                state.next_agent = "FINISH"  # 强制结束流程
                return state

        return wrapped_call


# 全局工作流实例
multi_agent_workflow_instance: Optional[MultiAgentWorkflow] = None


async def get_multi_agent_workflow() -> MultiAgentWorkflow:
    global multi_agent_workflow_instance
    if multi_agent_workflow_instance is None:
        multi_agent_workflow_instance = MultiAgentWorkflow()
        await multi_agent_workflow_instance.initialize_agents()  # 确保在获取时初始化
        multi_agent_workflow_instance.build_workflow()  # 构建工作流
    return multi_agent_workflow_instance
