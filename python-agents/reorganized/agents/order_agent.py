import os
import sys
from typing import Dict, Any, Optional, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent

# 修正导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from config import Config

# 模拟订单数据库和工具函数 (这部分保持不变)
orders = {}


def create_order(input: str) -> str:
    # ... (省略内部实现)
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
    # ... (省略内部实现)
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
    # ... (省略内部实现)
    if order_id not in orders:
        return f"订单 {order_id} 不存在。"
    status = orders[order_id]["status"]
    return f"订单 {order_id} 当前状态：{status}"


def logistics_query(order_id: str) -> str:
    # ... (省略内部实现)
    status = query_order_status(order_id).split("：")[-1]
    if status == "未支付":
        return f"订单 {order_id} 当前状态为 {status}，暂不提供物流信息。"
    logistics_info = {
        "已发货": f"订单 {order_id} 的物流信息：快递单号 KDS982734，正在运输中，预计明天送达。",
        "已签收": f"订单 {order_id} 已于 2025年7月1日 15:30 签收，签收人：李小明。",
    }
    return logistics_info.get(status, f"订单 {order_id} 当前状态为 {status}，暂无物流信息。")


def refund_order(order_id: str) -> str:
    # ... (省略内部实现)
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
    # ... (省略内部实现)
    if order_id not in orders:
        return f"订单 {order_id} 不存在。"
    if orders[order_id]["status"] == "未支付":
        orders[order_id]["status"] = "已支付"
        return f"订单 {order_id} 已成功支付。"
    else:
        return f"订单 {order_id} 当前状态为 {orders[order_id]['status']}，无需再次支付。"


def get_order_tools():
    # ... (省略内部实现)
    return [
        Tool(name="CreateOrder", func=create_order, description="创建新订单，参数格式：商品名称,数量,收货地址,支付方式"),
        Tool(name="ModifyOrder", func=modify_order,
             description="修改订单信息，参数格式：订单ID,修改内容（如：收货地址=北京市朝阳区）"),
        Tool(name="QueryOrderStatus", func=query_order_status, description="查询订单状态，参数：订单ID"),
        Tool(name="LogisticsQuery", func=logistics_query, description="查询物流信息，参数：订单ID"),
        Tool(name="RefundOrder", func=refund_order, description="取消订单并退款，参数：订单ID"),
        Tool(name="MarkOrderAsPaid", func=mark_order_as_paid, description="标记订单为已支付，参数：订单ID")
    ]


# ----------------------------------------------------------------------

class OrderAgent:
    _agent_executor: Optional[AgentExecutor] = None

    def __init__(self):
        """
        初始化一个无状态的 OrderAgent Executor。
        """
        llm = ChatOpenAI(
            api_key=Config.SILICONFLOW_API_KEY,
            base_url=Config.SILICONFLOW_API_BASE,
            model=Config.LLM_MODEL_NAME,
            temperature=Config.LLM_TEMPERATURE
        )
        tools = get_order_tools()
        system_message = SystemMessage(
            content="你是一个订单处理助手。请务必结合完整的对话历史来理解用户的意图，例如，如果用户在前面讨论过某个商品，现在说‘下单’，你应该知道是对哪个商品下单。你的职责包括：1. 支持查询订单状态、物流信息。2. 支持创建、修改、取消、退款订单。3. 无法回答的问题直接告知用户。4. 对话简洁友好。")

        prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

        self._agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
        )
        print("OrderAgent initialized with a stateless executor.")

    async def process_message(self, user_input: str, session_id: str, chat_history: List[BaseMessage]) -> str:
        """
        处理用户消息，使用传入的全局 chat_history 作为记忆。
        """
        print(f"--- OrderAgent 正在处理请求 (Session: {session_id}) ---")
        print(f"--- 接收到的全局历史记录 (最近3条): {chat_history[-3:]}")

        try:
            response = await self._agent_executor.ainvoke({
                "input": user_input,
                "chat_history": chat_history
            })
            output = response.get("output", "未能生成有效响应")
            return str(output)
        except Exception as e:
            error_msg = f"OrderAgent 在处理请求时出错: {str(e)}"
            print(f"ERROR: {error_msg}")
            return error_msg


# 全局 OrderAgent 实例
order_agent_instance: Optional['OrderAgent'] = None


async def get_order_agent() -> 'OrderAgent':
    global order_agent_instance
    if order_agent_instance is None:
        order_agent_instance = OrderAgent()
    return order_agent_instance
