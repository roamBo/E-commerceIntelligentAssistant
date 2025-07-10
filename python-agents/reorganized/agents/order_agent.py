import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
import redis

# 修正导入路径，确保能正确导入 config
# 如果 config.py 在项目根目录，而 agents 目录是其子目录，则需要这样调整
# 否则，请根据您的实际项目结构调整 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
import sys
sys.path.append(project_root)

from config import Config

print(f"Config.REDIS_URL: {Config.REDIS_URL}")

# 模拟订单数据库
orders = {}

# ----------------------------------------------------------------------
# 以下是 OrderAgent 内部的工具定义，直接放在这里以避免额外的文件依赖
# ----------------------------------------------------------------------
def create_order(input: str) -> str:
    """创建新订单，参数格式：商品名称,数量,收货地址,支付方式"""
    try:
        product_name, quantity, address, payment_method = input.split(',', 3)
        quantity = int(quantity.strip())
    except ValueError:
        return "参数格式错误，请使用：商品名称,数量，收货地址，支付方式"

    order_id = f"ORD-{hash(product_name + address) % 1000000:06d}"
    orders[order_id] = {
        "product_name": product_name.strip(),
        "quantity": quantity,
        "address": address.strip(),
        "payment_method": payment_method.strip(),
        "status": "未支付"
    }
    return (f"已成功创建订单 {order_id}，当前状态：未支付\n"
            f"- 商品: {product_name.strip()} x {quantity}\n"
            f"- 收货地址: {address.strip()}\n"
            f"- 支付方式: {payment_method.strip()}\n\n"
            "你可以使用订单ID查询订单状态或物流信息。")

def modify_order(input: str) -> str:
    """修改订单信息，参数格式：订单ID,修改内容（如：收货地址=北京市朝阳区）"""
    try:
        order_id, modification = input.split(',', 1)
        if order_id not in orders:
            return f"订单 {order_id} 不存在。"
        key, value = modification.strip().split('=')
        if key in orders[order_id]:
            orders[order_id][key] = value
            return f"订单 {order_id} 的{key}已修改为 {value}。"
        else:
            return f"订单 {order_id} 没有 {key} 这个字段。"
    except ValueError:
        return "参数格式错误，请使用：订单ID,修改内容"

def query_order_status(order_id: str) -> str:
    """查询订单状态，参数：订单ID"""
    if order_id not in orders:
        return f"订单 {order_id} 不存在。"
    status = orders[order_id]["status"]
    return f"订单 {order_id} 当前状态：{status}"

def logistics_query(order_id: str) -> str:
    """查询物流信息，参数：订单ID"""
    status = query_order_status(order_id).split("：")[-1]
    if status == "未支付":
        return f"订单 {order_id} 当前状态为 {status}，暂不提供物流信息。"
    logistics_info = {
        "已发货": f"订单 {order_id} 的物流信息：快递单号 KDS982734，正在运输中，预计明天送达。",
        "已签收": f"订单 {order_id} 已于 2025年7月1日 15:30 签收，签收人：李小明。",
    }
    return logistics_info.get(status, f"订单 {order_id} 当前状态为 {status}，暂无物流信息。")

def refund_order(order_id: str) -> str:
    """取消订单并退款，参数：订单ID"""
    if order_id not in orders:
        return f"订单 {order_id} 不存在。"
    status = orders[order_id]["status"]
    if status in ["已取消", "已签收"]:
        return f"订单 {order_id} 当前状态为 {status}，无法办理退款。"
    if status == "未支付":
        orders[order_id]["status"] = "已取消"
        return f"订单 {order_id} 已成功取消。"
    # 这里可以添加实际的退款逻辑
    orders[order_id]["status"] = "已取消"
    return f"订单 {order_id} 已成功取消，退款将在3-5个工作日内退回原支付账户。"

def mark_order_as_paid(order_id: str) -> str:
    """标记订单为已支付"""
    if order_id not in orders:
        return f"订单 {order_id} 不存在。"
    if orders[order_id]["status"] == "未支付":
        orders[order_id]["status"] = "已支付"
        return f"订单 {order_id} 已成功支付。"
    else:
        return f"订单 {order_id} 当前状态为 {orders[order_id]['status']}，无需再次支付。"

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
        ),
        Tool(
            name="MarkOrderAsPaid",
            func=mark_order_as_paid,
            description="标记订单为已支付，参数：订单ID"
        )
    ]

# ----------------------------------------------------------------------

class OrderAgent:
    _agent_executors_cache: Dict[str, AgentExecutor] = {} # 新增缓存

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=Config.SILICONFLOW_API_KEY,
            base_url=Config.SILICONFLOW_API_BASE,
            model=Config.LLM_MODEL_NAME,
            temperature=Config.LLM_TEMPERATURE
        )
        self.tools = get_order_tools()  # 使用 OrderAgent 自己的工具
        system_message_str = "你是一个订单处理助手，负责解答用户的订单问题：1. 支持查询订单状态、物流信息、预计送达时间等。创建订单时默认状态为未支付。2. 当用户询问物流时，自动调用LogisticsQuery工具（需先确认订单ID)。3. 支持创建、修改、取消、退款订单，查询订单状态，标记订单为已支付。4. 无法回答的问题直接告知用户。5. 对话简洁友好，每次回复不超过3句话。"
        system_message = SystemMessage(content=system_message_str)
        self.prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        print("OrderAgent initialized.")

    async def _get_agent_executor(self, session_id: str) -> AgentExecutor:
        """
        根据 session_id 获取或创建 AgentExecutor 实例。
        """
        if session_id not in self._agent_executors_cache:
            print(f"--- 为新会话创建 OrderAgent Executor: {session_id} ---")
            message_history = RedisChatMessageHistory(
                session_id=f"order_agent_history:{session_id}", # 确保 session_id 唯一
                url=Config.REDIS_URL
            )
            memory = ConversationBufferWindowMemory(
                chat_memory=message_history,
                memory_key="chat_history",
                return_messages=True,
                k=5
            )
            executor = AgentExecutor(
                agent=create_tool_calling_agent(
                    llm=self.llm,
                    tools=self.tools,
                    prompt=self.prompt
                ),
                tools=self.tools,
                verbose=True,
                memory=memory
            )
            self._agent_executors_cache[session_id] = executor
        else:
            print(f"--- 使用现有 OrderAgent Executor: {session_id} ---")
        return self._agent_executors_cache[session_id]

    async def process_message(self, user_input: str, session_id: str) -> str:
        """
        处理用户消息并返回 Agent 的响应。
        """
        agent_executor = await self._get_agent_executor(session_id)

        try:
            # 调用 AgentExecutor
            # 【修正】移除 chat_history: []，让 memory 自动管理
            response = await agent_executor.ainvoke({"input": user_input})
            output = response.get("output", "未能生成有效响应")

            # 【临时调试】强制确保返回字符串，并打印类型
            if not isinstance(output, str):
                print(f"WARNING: OrderAgent.process_message received non-string output: {output}, type: {type(output)}")
                output = str(output) if output is not None else "OrderAgent 返回了非字符串结果。"

            print(f"DEBUG: OrderAgent.process_message returning: {output}, type: {type(output)}")
            return output
        except Exception as e:
            error_msg = f"处理请求时出错: {str(e)}"
            print(f"DEBUG: OrderAgent.process_message error: {error_msg}")
            return error_msg

order_agent_instance: Optional['OrderAgent'] = None
async def get_order_agent() -> 'OrderAgent':
    global order_agent_instance
    if order_agent_instance is None:
        order_agent_instance = OrderAgent()
    return order_agent_instance
