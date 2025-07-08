# agents/order_agent.py
import os
import json
import asyncio  # 【新增】用于异步包装
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse  # 【新增】用于解析 Redis URL

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, Tool
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory  # 用于临时构建历史
import redis
from config import Config  # 导入 Config


# ----------------------------------------------------------------------
# 以下是 OrderAgent 内部的工具定义，直接放在这里以避免额外的文件依赖
# ----------------------------------------------------------------------
def create_order(input: str) -> str:
    """创建新订单，参数格式：商品名称,数量,收货地址,支付方式"""
    try:
        product_name, quantity, address, payment_method = input.split(',', 3)
        quantity = int(quantity.strip())
    except ValueError:
        return "参数格式错误，请使用：商品名称,数量,收货地址,支付方式"

    order_id = f"ORD-{hash(product_name + address) % 1000000:06d}"
    return (f"已成功创建订单 {order_id} 并完成支付：\n"
            f"- 商品: {product_name.strip()} x {quantity}\n"
            f"- 收货地址: {address.strip()}\n"
            f"- 支付方式: {payment_method.strip()}\n\n"
            "你可以使用订单ID查询订单状态或物流信息。")


def modify_order(input: str) -> str:
    """修改订单信息，参数格式：订单ID,修改内容（如：收货地址=北京市朝阳区）"""
    try:
        order_id, modification = input.split(',', 1)
        return f"订单 {order_id} 的{modification.strip()}已修改成功。"
    except ValueError:
        return "参数格式错误，请使用：订单ID,修改内容"


def query_order_status(order_id: str) -> str:
    """查询订单状态，参数：订单ID"""
    statuses = ["已支付", "已发货", "已签收", "已取消"]  # 移除未支付状态
    status = statuses[hash(order_id) % len(statuses)]
    return f"订单 {order_id} 当前状态：{status}"


def logistics_query(order_id: str) -> str:
    """查询物流信息，参数：订单ID"""
    status = query_order_status(order_id).split("：")[-1]
    logistics_info = {
        "已发货": f"订单 {order_id} 的物流信息：快递单号 KDS982734，正在运输中，预计明天送达。",
        "已签收": f"订单 {order_id} 已于 2025年7月1日 15:30 签收，签收人：李小明。",
    }
    return logistics_info.get(status, f"订单 {order_id} 当前状态为 {status}，暂无物流信息。")


def refund_order(order_id: str) -> str:
    """取消订单并退款，参数：订单ID"""
    status = query_order_status(order_id).split("：")[-1]
    if status in ["已取消", "已签收"]:
        return f"订单 {order_id} 当前状态为 {status}，无法办理退款。"
    return f"订单 {order_id} 已成功取消，退款将在3-5个工作日内退回原支付账户。"


def get_order_tools():
    """获取所有工具列表"""
    return [
        Tool(
            name="CreateOrder",
            func=create_order,
            description="创建新订单，参数格式：商品名称,数量,收货地址,支付方式"
        ),
        Tool(
            name="ModifyOrder",
            func=modify_order,
            description="修改订单信息，参数格式：订单ID,修改内容（如：收货地址=北京市朝阳区）"
        ),
        Tool(
            name="QueryOrderStatus",
            func=query_order_status,
            description="查询订单状态，参数：订单ID"
        ),
        Tool(
            name="LogisticsQuery",
            func=logistics_query,
            description="查询物流信息，参数：订单ID"
        ),
        Tool(
            name="RefundOrder",
            func=refund_order,
            description="取消订单并退款，参数：订单ID"
        )
    ]


# ----------------------------------------------------------------------

# Redis 客户端，使用 Config 中的 REDIS_URL
# 注意：这里假设 OrderAgent 内部的 Redis 客户端是独立的，
# 并且每个 session_id 对应一个独立的 chat_history key。
parsed_redis_url = urlparse(Config.REDIS_URL)
redis_client = redis.Redis(
    host=parsed_redis_url.hostname,
    port=parsed_redis_url.port,
    db=int(parsed_redis_url.path.lstrip('/')) if parsed_redis_url.path else 0,
    password=parsed_redis_url.password if parsed_redis_url.password else None
)


class OrderAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=Config.SILICONFLOW_API_KEY,
            base_url=Config.SILICONFLOW_API_BASE,
            model=Config.LLM_MODEL_NAME,
            temperature=Config.LLM_TEMPERATURE
        )
        self.tools = get_order_tools()  # 使用 OrderAgent 自己的工具
        # self.message_history 在 process_message 中按 session_id 动态加载
        system_message_str = "你是一个订单处理助手，负责解答用户的订单问题：1. 支持查询订单状态、物流信息、预计送达时间等。创建订单时默认已完成支付。2. 当用户询问物流时，自动调用LogisticsQuery工具（需先确认订单ID)。3. 支持创建、修改、取消、退款订单，查询订单状态。4. 无法回答的问题直接告知用户。5. 对话简洁友好，每次回复不超过3句话。"
        system_message = SystemMessage(content=system_message_str)
        self.prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        # self.agent 在 process_message 中按 session_id 动态创建或更新
        print("OrderAgent initialized.")

    def _tools_to_functions(self) -> list:
        # 适配 LangChain 0.1.x 的函数绑定方式
        return [{
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "工具输入参数"}
                },
                "required": ["input"]
            }
        } for tool in self.tools]

    async def process_message(self, user_input: str, session_id: str) -> str:
        """
        处理用户消息并返回 Agent 的响应。
        """
        # 每次调用时，加载当前 session 的历史，并创建 AgentExecutor
        message_history_for_session = self._load_chat_history(session_id)

        # 重新初始化 AgentExecutor，确保使用最新的 chat_history
        # 注意：这里每次都重新创建 AgentExecutor，效率较低，
        # 更优方案是修改 OrderAgent 内部，使其支持 LangChain 的 ConversationBufferWindowMemory
        # 但为了“尽可能不修改原有代码”，我们采取这种适配方式。
        agent_executor = self._initialize_agent(message_history_for_session.messages)

        try:
            message_history_for_session.add_user_message(user_input)
            # 使用 ainvoke 进行异步调用
            response = await agent_executor.ainvoke({"input": user_input})

            output = response.get("output", "未能生成有效响应")
            message_history_for_session.add_ai_message(output)
            self._save_chat_history(session_id, message_history_for_session.messages)
            return output
        except Exception as e:
            error_msg = f"处理请求时出错: {str(e)}"
            message_history_for_session.add_ai_message(error_msg)
            self._save_chat_history(session_id, message_history_for_session.messages)
            return error_msg

    def _save_chat_history(self, session_id: str, messages: List[BaseMessage]):
        try:
            redis_key = f'order_chat_history:{session_id}'  # 区分 key
            history = []
            for message in messages:
                if isinstance(message, HumanMessage):
                    history.append({"type": "human", "data": {"content": message.content}})
                elif isinstance(message, AIMessage):
                    history.append({"type": "ai", "data": {"content": message.content}})
            redis_client.set(redis_key, json.dumps(history))
        except Exception as e:
            print(f"保存对话历史失败: {str(e)}")

    def _load_chat_history(self, session_id: str) -> ChatMessageHistory:
        """从 Redis 加载指定 session_id 的对话历史"""
        message_history = ChatMessageHistory()
        try:
            redis_key = f'order_chat_history:{session_id}'  # 区分 key
            history_data = redis_client.get(redis_key)
            if history_data:
                history = json.loads(history_data)
                for item in history:
                    if item["type"] == "human":
                        message_history.add_user_message(item["data"]["content"])
                    elif item["type"] == "ai":
                        message_history.add_ai_message(item["data"]["content"])
        except Exception as e:
            print(f"加载对话历史失败: {str(e)}")
        return message_history

    def clear_chat_history(self, session_id: str):
        try:
            redis_key = f'order_chat_history:{session_id}'  # 区分 key
            redis_client.delete(redis_key)
            print(f"会话 {session_id} 的订单聊天记录已清空。")
        except Exception as e:
            print(f"清空聊天记录失败: {str(e)}")


# 全局 OrderAgent 实例
order_agent_instance: Optional['OrderAgent'] = None


async def get_order_agent() -> 'OrderAgent':
    global order_agent_instance
    if order_agent_instance is None:
        order_agent_instance = OrderAgent()
    return order_agent_instance
