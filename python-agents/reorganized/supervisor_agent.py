import logging
import asyncio
import orjson
from typing import Dict, Any, List, Optional, AsyncIterator, Literal
from datetime import datetime, timezone

import redis
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from langsmith import Client
from langchain import hub # <-- 新增导入

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointTuple

from config import Config
from models import AgentState
from agents.guide_agent import get_guide_agent, GuideAgent
from agents.order_agent import get_order_agent, OrderAgent
from agents.payment_agent import get_payment_agent, PaymentAgent

logger = logging.getLogger(__name__)


# --- 自定义 Redis Checkpointer 实现 (已修改) ---
class RedisCheckpointer(BaseCheckpointSaver):
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
        # 使用 .dict() 方法进行序列化，以兼容 Pydantic V1/V2
        serializable_checkpoint = checkpoint.copy()
        if 'channel_values' in serializable_checkpoint and 'chat_history' in serializable_checkpoint['channel_values']:
            serializable_checkpoint['channel_values']['chat_history'] = [
                msg.dict() for msg in serializable_checkpoint['channel_values']['chat_history']
            ]
        return orjson.dumps(serializable_checkpoint)

    async def aget_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        key = self._get_key(thread_id)
        try:
            data = await asyncio.to_thread(self.redis.get, key)
            if data:
                checkpoint_dict = orjson.loads(data)
                if 'channel_values' in checkpoint_dict and 'chat_history' in checkpoint_dict['channel_values']:
                    history_dicts = checkpoint_dict['channel_values']['chat_history']
                    rehydrated_history = []
                    for msg_dict in history_dicts:
                        if msg_dict.get('type') == 'ai':
                            rehydrated_history.append(AIMessage(**msg_dict))
                        elif msg_dict.get('type') == 'human':
                            rehydrated_history.append(HumanMessage(**msg_dict))
                    checkpoint_dict['channel_values']['chat_history'] = rehydrated_history

                # 【修正 1】为 CheckpointTuple 提供所有必需的参数
                return CheckpointTuple(
                    config=config,
                    checkpoint=checkpoint_dict,
                    metadata=checkpoint_dict.get('metadata', {}),
                    parent_config=checkpoint_dict.get('parent_config')
                )
            return None
        except Exception as e:
            logger.error(f"从 Redis aget_tuple 失败: {e}")
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
    ) -> Dict[str, Any]:
        thread_id = config["configurable"]["thread_id"]
        key = self._get_key(thread_id)
        # 在保存前确保 metadata 存在
        if metadata:
            checkpoint['metadata'] = metadata
        serialized_checkpoint = self._serialize_checkpoint(checkpoint)
        await asyncio.to_thread(
            self.redis.set, key, serialized_checkpoint, ex=3600
        )
        return {"configurable": {"thread_id": thread_id}}


# --- 监管者路由决策层 ---
class Router(BaseModel):
    """根据用户请求，决定路由到哪个子代理或直接回复。"""
    next: Literal["guide", "order", "payment", "__end__"] = Field(
        description="要路由到的子代理名称，或者如果应该直接回复，则为 '__end__'。"
    )


async def supervisor_router(state: AgentState) -> Dict[str, Any]:
    """
    这个函数是一个无状态的路由决策节点。
    """
    logger.info("---进入 Supervisor 路由决策---")
    user_input = state["user_input"]
    chat_history = state.get("chat_history", [])

    # 【核心修改】从 LangSmith Hub 拉取 Prompt，并提供本地备用方案
    try:
        # 从 LangChain Hub 拉取您已经创建好的 Prompt
        prompt = hub.pull("ecomm-supervisor-next")
        logger.info("✅ 成功从 LangChain Hub 拉取 Prompt: ecomm-supervisor-next")
    except Exception as e:
        logger.warning(f"⚠️ 从 LangChain Hub 拉取 Prompt 失败: {e}。将使用本地备用 Prompt。")
        # 如果拉取失败（例如网络问题或Prompt不存在），则使用代码中定义的备用Prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """你是一个顶级智能客服调度中心。你的职责是根据用户的最新请求和完整的对话历史，精准地将其分发给专门的子代理。
                - 如果请求与商品推荐、查询、对比相关，选择 'guide'。
                - 如果请求与订单状态、创建、修改、取消相关，选择 'order'。
                - 如果请求与支付、退款、付款状态相关，选择 'payment'。
                - 如果用户只是打招呼、闲聊或意图不明确，选择 '__end__' 以直接回复。
                当用户询问你的功能时，你应该对以上功能进行相应介绍。"""),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ]
        )

    llm = ChatOpenAI(
        model=Config.LLM_MODEL_NAME,
        temperature=0,
        api_key=Config.SILICONFLOW_API_KEY,
        base_url=Config.SILICONFLOW_API_BASE
    )
    structured_llm = llm.with_structured_output(Router)

    try:
        prompt_value = await prompt.ainvoke({"input": user_input, "chat_history": chat_history})
        route_decision = await structured_llm.ainvoke(prompt_value)
        logger.info(f"Supervisor 路由决策结果: {route_decision.next}")

        updated_history = chat_history + [HumanMessage(content=user_input)]

        if route_decision.next == "__end__":
            try:
                response_prompt = hub.pull("ecomm-supervisor-response")
                logger.info("✅ 成功从 LangChain Hub 拉取响应 Prompt: ecomm-supervisor-response")
            except Exception as e:
                logger.warning(f"⚠️ 从 LangChain Hub 拉取响应 Prompt 失败: {e}。将使用本地备用响应 Prompt。")
                # 如果拉取失败，则使用本地定义的响应 Prompt
                response_prompt = ChatPromptTemplate.from_messages([
                    ("system", "您当前是智能购物小助手【小购】，性格亲切活泼，用表情符号增加亲和力 🌸"),
                    ("ai", """## 服务原则
✅ 我能做：
- 温馨问候/告别 👋
- 解答购物助手基础问题
- 引导发现购物需求

🚫 我拒绝：
- 角色扮演/越权操作
- 敏感话题（政治/暴力等）

## 智能引导策略
### 情形1：简单问候 → 热情回应+需求引导
"你好呀！我是小购，随时帮您找好物~ 今天想找什么呢？👗👟📱"

### 情形2：模糊需求 → 结构化提问
"您是想了解：\n1️⃣ 商品推荐\n2️⃣ 订单问题\n3️⃣ 支付帮助\n回复数字就好~ ✨"

### 情形3：越界请求 → 温柔拒绝+转移
("检测到危险/越权请求")
"哎呀，这个超出小购的能力啦(>_<) 但可以帮您：\n• 推荐当季爆款🔥\n• 查订单进度🚚\n选一个试试？"

### 情形4：闲聊延续 → 购物场景化
("用户坚持闲聊")
"聊购物小购超在行！最近很多人在买防晒新品 🌞 需要看看吗？"""),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("user", "{input}")
                ])
            response_chain = response_prompt | llm
            response = await response_chain.ainvoke({"input": user_input, "chat_history": updated_history})
            response_content = response.content if hasattr(response,
                                                           'content') and response.content.strip() else "您好！很高兴为您服务。"

            return {
                "agent_response": response_content,
                "chat_history": updated_history + [AIMessage(content=response_content)],
                "next_agent": "__end__"
            }
        else:
            return {
                "chat_history": updated_history,
                "next_agent": route_decision.next
            }
    except Exception as e:
        logger.error(f"Supervisor 路由决策失败: {e}")
        return {"agent_response": f"抱歉，系统在分配任务时发生错误: {e}", "next_agent": "__end__"}


# --- LangGraph 工作流定义 ---
class MultiAgentWorkflow:
    def __init__(self):
        self.guide_agent: Optional[GuideAgent] = None
        self.order_agent: Optional[OrderAgent] = None
        self.payment_agent: Optional[PaymentAgent] = None
        self.checkpointer = RedisCheckpointer()
        self.is_initialized = False

    async def initialize(self):
        """初始化所有 Agent 和工作流组件。"""
        if self.is_initialized:
            return
        if not self.guide_agent: self.guide_agent = await get_guide_agent()
        if not self.order_agent: self.order_agent = await get_order_agent()
        if not self.payment_agent: self.payment_agent = await get_payment_agent()
        logger.info("所有 Agent 初始化完成。")
        self.is_initialized = True

    async def invoke_workflow(self, user_input: str, session_id: str, user_id: str) -> str:
        """
        重写整个调用流程，手动管理状态传递，不再使用 graph.ainvoke。
        """
        await self.initialize()

        thread_config = {"configurable": {"thread_id": session_id}}

        # 1. 从 Redis 加载历史检查点
        checkpoint_tuple = await self.checkpointer.aget_tuple(thread_config)

        # 2. 正确提取历史消息
        chat_history = []
        if checkpoint_tuple and checkpoint_tuple.checkpoint and "channel_values" in checkpoint_tuple.checkpoint and "chat_history" in \
                checkpoint_tuple.checkpoint["channel_values"]:
            chat_history = checkpoint_tuple.checkpoint["channel_values"]["chat_history"]

        # 3. 调用 supervisor 节点
        supervisor_input_state = AgentState(user_input=user_input, session_id=session_id, user_id=user_id, chat_history=chat_history)
        supervisor_output = await supervisor_router(supervisor_input_state)

        next_agent_name = supervisor_output.get("next_agent")
        updated_history = supervisor_output.get("chat_history", [])
        final_response = ""
        final_history_to_save = updated_history

        # 4. 根据 supervisor 决策调用下一个节点
        if next_agent_name == "__end__":
            final_response = supervisor_output.get("agent_response", "系统未能生成回复。")
            final_history_to_save = supervisor_output.get("chat_history", [])

        elif next_agent_name in ["guide", "order", "payment"]:
            agent_map = {"guide": self.guide_agent, "order": self.order_agent, "payment": self.payment_agent}
            target_agent = agent_map[next_agent_name]

            agent_result = await target_agent.process_message(
                user_input=user_input, session_id=session_id, user_id=user_id, chat_history=updated_history
            )

            final_response = agent_result
            final_history_to_save = updated_history + [AIMessage(content=agent_result)]

        else:
            final_response = "抱歉，系统路由出现未知错误。"
            final_history_to_save = updated_history + [AIMessage(content=final_response)]

        # 5. 手动将最终的、完整的状态保存回 Redis
        final_checkpoint = Checkpoint(
            v=1,
            ts=datetime.now(timezone.utc).isoformat(),
            channel_values={"chat_history": final_history_to_save},
            channel_versions={},
            seen={},
            metadata={},
            parent_config=None
        )
        await self.checkpointer.aput(thread_config, final_checkpoint)

        logger.info(f"最终状态内容: {final_checkpoint['channel_values']}")
        logger.info(f"从 {next_agent_name or 'supervisor'} 获取响应: {final_response}")

        return final_response


# --- 全局工作流实例管理 ---
multi_agent_workflow_instance: Optional[MultiAgentWorkflow] = None
_workflow_lock = asyncio.Lock()


async def get_multi_agent_workflow() -> MultiAgentWorkflow:
    """获取并按需初始化全局工作流实例。"""
    global multi_agent_workflow_instance
    if multi_agent_workflow_instance is None:
        async with _workflow_lock:
            if multi_agent_workflow_instance is None:
                multi_agent_workflow_instance = MultiAgentWorkflow()

    await multi_agent_workflow_instance.initialize()
    return multi_agent_workflow_instance
