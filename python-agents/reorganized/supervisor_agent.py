# supervisor_agent.py

import logging
import asyncio
import orjson
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime, timezone

import redis
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointTuple

from config import Config
from models import AgentState, ChatRequest
from agents.guide_agent import get_guide_agent, GuideAgent
from agents.order_agent import get_order_agent, OrderAgent
from agents.payment_agent import get_payment_agent, PaymentAgent

logger = logging.getLogger(__name__)


# --- 自定义 Redis Checkpointer 实现 (最终正确版) ---
class RedisCheckpointer(BaseCheckpointSaver):
    """
    一个将检查点保存到 Redis 的 LangGraph Checkpointer。
    【最终正确版】: 解决了 BaseMessage 对象的 JSON 序列化问题。
    """

    def __init__(self):
        super().__init__()
        try:
            self.redis = redis.Redis.from_url(Config.REDIS_URL, decode_responses=False)
            self.redis.ping()
            logger.info(f"✅ RedisCheckpointer: 成功连接到 Redis 服务器: {Config.REDIS_URL}")
        except redis.ConnectionError as e:
            logger.error(f"❌ RedisCheckpointer: 无法连接到 Redis 服务器: {Config.REDIS_URL}. 错误详情: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ RedisCheckpointer: 初始化失败: {e}")
            raise

    def _get_key(self, thread_id: str) -> str:
        return f"langgraph:checkpoint:{thread_id}"

    def _serialize_checkpoint(self, checkpoint: Checkpoint) -> bytes:
        """
        【核心修正】: 为 orjson.dumps 提供一个 default 函数来处理 BaseMessage 对象。
        """

        def default_serializer(obj):
            # 如果对象是 BaseMessage 的实例，将其转换为字典
            if isinstance(obj, BaseMessage):
                return obj.dict()
            # 对于其他无法序列化的类型，抛出错误
            raise TypeError(f"Type is not JSON serializable: {type(obj).__name__}")

        # 使用 orjson.dumps 并传入自定义的 default 函数
        return orjson.dumps(checkpoint, default=default_serializer)

    async def aget_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        key = self._get_key(thread_id)
        try:
            data = await asyncio.to_thread(self.redis.get, key)
            if data:
                # LangGraph 的默认反序列化器可以处理从 .dict() 转换回来的对象
                checkpoint = self.serializer.loads(data)
                return CheckpointTuple(config=config, checkpoint=checkpoint)
            return None
        except Exception:
            await asyncio.to_thread(self.redis.delete, key)
            return None

    async def alist(self, config: Optional[Dict[str, Any]] = None) -> AsyncIterator[CheckpointTuple]:
        thread_id_prefix = "langgraph:checkpoint:"
        keys_iterator = asyncio.to_thread(self.redis.scan_iter, f"{thread_id_prefix}*")
        async for key_bytes in keys_iterator:
            key = key_bytes.decode('utf-8')
            thread_id = key[len(thread_id_prefix):]
            if tuple_data := await self.aget_tuple({"configurable": {"thread_id": thread_id}}):
                yield tuple_data

    async def aput(
            self,
            config: Dict[str, Any],
            checkpoint: Checkpoint,
            metadata: Optional[Dict[str, Any]] = None,
            new_writes: Optional[List[tuple[str, Any]]] = None
    ) -> Dict[str, Any]:
        thread_id = config["configurable"]["thread_id"]
        key = self._get_key(thread_id)
        # 使用我们修正后的序列化方法
        serialized_checkpoint = self._serialize_checkpoint(checkpoint)
        await asyncio.to_thread(
            self.redis.set, key, serialized_checkpoint, ex=3600
        )
        return {"configurable": {"thread_id": thread_id}}

    async def aput_writes(
            self, config: Dict[str, Any], writes: List[tuple[str, Any]], task_id: str
    ) -> Dict[str, Any]:
        current_checkpoint_tuple = await self.aget_tuple(config)
        if current_checkpoint_tuple:
            checkpoint = current_checkpoint_tuple.checkpoint
        else:
            checkpoint = Checkpoint(v=1, ts=datetime.now(timezone.utc).isoformat(), channel_values={},
                                    channel_versions={}, seen={})

        for channel, value in writes:
            checkpoint["channel_values"][channel] = value
            checkpoint["channel_versions"][channel] = checkpoint["channel_versions"].get(channel, 0) + 1

        return await self.aput(config, checkpoint)


# --- 1. 定义监管者 Agent 的工具 ---
class SupervisorTools:
    def __init__(self, guide_agent: GuideAgent, order_agent: OrderAgent, payment_agent: PaymentAgent):
        self.guide_agent = guide_agent
        self.order_agent = order_agent
        self.payment_agent = payment_agent

    def get_tools(self):
        return [
            StructuredTool.from_function(
                name="guide_agent_process_message",
                func=self.guide_agent.process_message,
                args_schema=ChatRequest,
                description="""当用户需要商品推荐、商品信息查询、产品对比等购物辅助信息时使用。
                                输入参数: 一个包含 'user_input' (str) 和 'session_id' (str) 的 JSON 对象。
                                返回商品推荐报告或相关购物信息。"""
            ),
            StructuredTool.from_function(
                name="order_agent_process_message",
                func=self.order_agent.process_message,
                args_schema=ChatRequest,
                description="""当用户需要查询订单状态、物流信息、创建订单、修改订单、取消订单、申请退款等订单相关操作时使用。
                                输入参数: 一个包含 'user_input' (str) 和 'session_id' (str) 的 JSON 对象。
                                返回订单处理结果或相关订单信息。"""
            ),
            StructuredTool.from_function(
                name="payment_agent_process_message",
                func=self.payment_agent.process_message,
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
            ("system", """你是一个顶级智能客服调度中心。你的职责是根据用户的请求，精准地将其分发给专门的子代理。
                        你拥有以下三个子代理工具：
                        - `guide_agent_process_message`: 负责所有与商品浏览和推荐相关的任务。
                        - `order_agent_process_message`: 负责所有与订单管理（创建、查询、修改、取消）相关的任务。
                        - `payment_agent_process_message`: 负责所有与支付和退款相关的任务。

                        你的决策逻辑：
                        1.  分析用户输入的意图。
                        2.  如果意图明确匹配某个子代理的职责，你必须调用对应的工具。
                        3.  调用工具时，必须严格使用 `ChatRequest` 格式，包含 `user_input` 和 `session_id`。
                        4.  如果用户只是打招呼或意图不明确，请不要调用任何工具，而是直接回复，引导用户说出具体需求。
                        """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.supervisor_tools,
            prompt=self.prompt
        )
        self.agent_executor_instance = AgentExecutor(
            agent=agent,
            tools=self.supervisor_tools,
            verbose=True,
            handle_parsing_errors=True
        )
        logger.info("SupervisorAgent initialized.")

    async def route_user_request(self, state: AgentState) -> Dict[str, Any]:
        user_input = state["user_input"]
        session_id = state["session_id"]
        chat_history = state.get("chat_history", [])

        try:
            response = await self.agent_executor_instance.ainvoke({
                "input": user_input,
                "chat_history": chat_history
            })

            if "tool_calls" in response and response["tool_calls"]:
                tool_call = response["tool_calls"][0]
                tool_name = tool_call["name"]
                logger.info(f"SupervisorAgent 决定路由到: {tool_name}")

                state["next_agent"] = tool_name
                state["chat_history"].append(HumanMessage(content=user_input))
                state["chat_history"].append(
                    AIMessage(content=f"好的，正在为您转接至{tool_name.replace('_process_message', '')}..."))
            else:
                output = response.get("output", "抱歉，我暂时无法理解您的意思，可以换个方式提问吗？")
                logger.info(f"SupervisorAgent 直接回答: {output}")
                state["agent_response"] = output
                state["next_agent"] = "FINISH"
                state["chat_history"].append(HumanMessage(content=user_input))
                state["chat_history"].append(AIMessage(content=output))

        except Exception as e:
            logger.exception(f"监管者 Agent 路由失败: {e}")
            error_message = f"抱歉，系统调度时发生错误，请稍后再试。错误详情: {e}"
            state["agent_response"] = error_message
            state["next_agent"] = "FINISH"
            state["chat_history"].append(HumanMessage(content=user_input))
            state["chat_history"].append(AIMessage(content=error_message))

        return state


# --- 3. LangGraph 工作流定义 ---
class MultiAgentWorkflow:
    def __init__(self):
        self.guide_agent: Optional[GuideAgent] = None
        self.order_agent: Optional[OrderAgent] = None
        self.payment_agent: Optional[PaymentAgent] = None
        self.supervisor_agent: Optional[SupervisorAgent] = None
        self.workflow: Optional[StateGraph] = None

    async def initialize_agents(self):
        if not self.guide_agent:
            self.guide_agent = await get_guide_agent()
        if not self.order_agent:
            self.order_agent = await get_order_agent()
        if not self.payment_agent:
            self.payment_agent = await get_payment_agent()
        if not self.supervisor_agent:
            self.supervisor_agent = SupervisorAgent(self.guide_agent, self.order_agent, self.payment_agent)
        logger.info("所有 Agent 初始化完成。")

    def build_workflow(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("supervisor", self.supervisor_agent.route_user_request)
        workflow.add_node("guide_agent_node",
                          self._create_agent_node("guide_agent_output", self.guide_agent.process_message))
        workflow.add_node("order_agent_node",
                          self._create_agent_node("order_agent_output", self.order_agent.process_message))
        workflow.add_node("payment_agent_node",
                          self._create_agent_node("payment_agent_output", self.payment_agent.process_message))

        workflow.set_entry_point("supervisor")

        def route_to_agent(state: AgentState):
            next_agent = state.get("next_agent")
            if next_agent == "guide_agent_process_message":
                return "guide_agent_node"
            if next_agent == "order_agent_process_message":
                return "order_agent_node"
            if next_agent == "payment_agent_process_message":
                return "payment_agent_node"
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
            checkpointer=RedisCheckpointer()
        )
        logger.info("LangGraph 工作流构建并编译完成。")

    async def invoke_workflow(self, user_input: str, session_id: str) -> str:
        if not self.workflow:
            await self.initialize_agents()
            self.build_workflow()

        thread_config = {"configurable": {"thread_id": session_id}}

        initial_state = AgentState(
            user_input=user_input,
            session_id=session_id,
            chat_history=[],
            agent_response=None,
            next_agent=None,
            guide_agent_output=None,
            order_agent_output=None,
            payment_agent_output=None,
        )

        try:
            final_state = None
            async for event in self.workflow.astream(initial_state, config=thread_config):
                if "supervisor" in event or "guide_agent_node" in event or "order_agent_node" in event or "payment_agent_node" in event:
                    final_state = event

            if not final_state:
                raise ValueError("工作流未能返回最终状态。")

            last_node_name = list(final_state.keys())[-1]
            final_agent_state = final_state[last_node_name]

            if final_agent_state.get("agent_response"):
                return final_agent_state["agent_response"]
            if final_agent_state.get("guide_agent_output"):
                return final_agent_state["guide_agent_output"]
            if final_agent_state.get("order_agent_output"):
                return final_agent_state["order_agent_output"]
            if final_agent_state.get("payment_agent_output"):
                return final_agent_state["payment_agent_output"]

            return "抱歉，系统未能处理您的请求，请稍后再试。"

        except Exception as e:
            logger.exception(f"LangGraph 工作流执行失败: {e}")
            return f"抱歉，系统在处理您的请求时发生严重错误: {e}"

    def _create_agent_node(self, output_key: str, agent_method):
        async def agent_node(state: AgentState) -> Dict[str, Any]:
            user_input = state["user_input"]
            session_id = state["session_id"]
            logger.info(f"调用子 Agent: {agent_method.__self__.__class__.__name__} for session {session_id}")

            try:
                result = await agent_method(user_input=user_input, session_id=session_id)
                state[output_key] = result
                state["chat_history"].append(AIMessage(content=result))
            except Exception as e:
                logger.exception(f"子 Agent 调用失败 ({agent_method.__name__}): {e}")
                error_message = f"抱歉，{agent_method.__self__.__class__.__name__} 在处理时遇到问题: {e}"
                state["agent_response"] = error_message
                state["chat_history"].append(AIMessage(content=error_message))

            return state

        return agent_node


# --- 全局工作流实例管理 ---
multi_agent_workflow_instance: Optional[MultiAgentWorkflow] = None
_workflow_lock = asyncio.Lock()


async def get_multi_agent_workflow() -> MultiAgentWorkflow:
    global multi_agent_workflow_instance
    async with _workflow_lock:
        if multi_agent_workflow_instance is None:
            multi_agent_workflow_instance = MultiAgentWorkflow()
            await multi_agent_workflow_instance.initialize_agents()
            multi_agent_workflow_instance.build_workflow()
    return multi_agent_workflow_instance
