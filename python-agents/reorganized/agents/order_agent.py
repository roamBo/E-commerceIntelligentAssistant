# agents/order_agent.py
import logging
import asyncio
import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent, Tool

from config import Config
from models import AgentState

# ----------------------------------------------------------------------
# 订单代理配置 (无变化)
# ----------------------------------------------------------------------
class OrderConfig:
    """订单代理配置"""
    SILICONFLOW_API_KEY: str = Config.SILICONFLOW_API_KEY
    SILICONFLOW_BASE_URL: str = Config.SILICONFLOW_API_BASE
    MODEL_NAME: str = Config.LLM_MODEL_NAME
    MODEL_TEMPERATURE: float = Config.LLM_TEMPERATURE
    MAX_TOKENS: int = 500
    ORDER_SERVICE_BASE_URL: str = os.environ.get("ORDER_SERVICE_BASE_URL", "http://10.172.66.224:8081/order"  )


# ----------------------------------------------------------------------
# 订单服务 API 封装 (无变化)
# ----------------------------------------------------------------------
class OrderServiceAPI:
    """订单服务 API 封装"""

    def __init__(self, base_url: str = OrderConfig.ORDER_SERVICE_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 120
        self.logger = logging.getLogger(__name__)

    async def create_order(self, user_id: str, products: List[Dict[str, Any]], status: str = "PENDING_PAYMENT") -> Dict[
        str, Any]:
        """创建新订单"""
        url = f"{self.base_url}/api/orders"
        data = {
            "userId": user_id,
            "products": products,
            "status": status
        }
        try:
            response = await asyncio.to_thread(self.session.post, url, json=data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"创建订单失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_all_orders(self) -> Dict[str, Any]:
        """获取所有订单"""
        url = f"{self.base_url}/api/orders"
        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取所有订单失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_order_by_id(self, order_id: str) -> Dict[str, Any]:
        """根据订单 ID 获取订单"""
        url = f"{self.base_url}/api/orders/{order_id}"
        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取订单信息失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_orders_by_user(self, user_id: str) -> Dict[str, Any]:
        """根据用户 ID 获取订单"""
        url = f"{self.base_url}/api/orders/user/{user_id}"
        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取用户订单失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def update_order(self, order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新订单"""
        url = f"{self.base_url}/api/orders/{order_id}"
        try:
            response = await asyncio.to_thread(self.session.put, url, json=order_data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"更新订单失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """更新订单状态"""
        url = f"{self.base_url}/api/orders/{order_id}/status/{status}"
        try:
            response = await asyncio.to_thread(self.session.patch, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"更新订单状态失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def delete_order(self, order_id: str) -> Dict[str, Any]:
        """删除订单"""
        url = f"{self.base_url}/api/orders/{order_id}"
        try:
            response = await asyncio.to_thread(self.session.delete, url)
            response.raise_for_status()
            return {"success": True, "data": response.json() if response.content else {}}
        except Exception as e:
            self.logger.error(f"删除订单失败: {str(e)}")
            return {"success": False, "error": str(e)}


# ----------------------------------------------------------------------
# 订单代理工具函数 (核心修改部分)
# ----------------------------------------------------------------------
def create_order_tool(order_agent):
    """创建订单工具"""

    def _create_order_sync(order_data: str) -> str:
        """同步包装器"""
        return asyncio.run(_create_order(order_data))

    async def _create_order(order_data: str) -> str:
        """创建新订单，参数为JSON格式字符串"""
        try:
            try:
                data = json.loads(order_data)
            except json.JSONDecodeError:
                return "参数格式错误。输入必须是包含 user_id 和 products 列表的JSON字符串。"
            user_id = data.get("user_id")
            products = data.get("products")
            if not all([user_id, products]):
                return "缺少必要参数：user_id、products"
            result = await order_agent.create_order(user_id, products)
            if result["success"]:
                return f"订单创建成功：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"订单创建失败：{result['error']}"
        except Exception as e:
            return f"创建订单时发生错误：{str(e)}"

    return Tool(
        name="create_order",
        func=_create_order_sync, # 【修改】提供一个同步函数
        coro=_create_order,      # 【修改】同时提供异步函数
        description="创建新订单。输入必须是包含 user_id 和 products 列表的JSON字符串。"
    )


def get_order_by_id_tool(order_agent):
    """根据ID获取订单工具"""

    def _get_order_by_id_sync(order_id: str) -> str:
        """同步包装器"""
        return asyncio.run(_get_order_by_id(order_id))

    async def _get_order_by_id(order_id: str) -> str:
        """根据订单ID获取订单信息"""
        try:
            result = await order_agent.get_order_by_id(order_id.strip())
            if result["success"]:
                return f"订单信息：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"获取订单信息失败：{result['error']}"
        except Exception as e:
            return f"获取订单信息时发生错误：{str(e)}"

    return Tool(
        name="get_order_by_id",
        func=_get_order_by_id_sync, # 【修改】提供一个同步函数
        coro=_get_order_by_id,      # 【修改】同时提供异步函数
        description="根据订单ID获取订单信息，参数：订单ID"
    )


def get_orders_by_user_tool(order_agent):
    """获取用户订单工具"""

    def _get_orders_by_user_sync(user_id: str) -> str:
        """同步包装器"""
        return asyncio.run(_get_orders_by_user(user_id))

    async def _get_orders_by_user(user_id: str) -> str:
        """根据用户ID获取所有订单"""
        try:
            result = await order_agent.get_orders_by_user(user_id.strip())
            if result["success"]:
                return f"用户订单列表：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"获取用户订单失败：{result['error']}"
        except Exception as e:
            return f"获取用户订单时发生错误：{str(e)}"

    return Tool(
        name="get_orders_by_user",
        func=_get_orders_by_user_sync, # 【修改】提供一个同步函数
        coro=_get_orders_by_user,      # 【修改】同时提供异步函数
        description="根据用户ID获取所有订单，参数：用户ID"
    )


def update_order_status_tool(order_agent):
    """更新订单状态工具"""

    def _update_order_status_sync(status_data: str) -> str:
        """同步包装器"""
        return asyncio.run(_update_order_status(status_data))

    async def _update_order_status(status_data: str) -> str:
        """更新订单状态，参数为JSON格式字符串"""
        try:
            try:
                data = json.loads(status_data)
            except json.JSONDecodeError:
                return "参数格式错误。输入必须是包含 order_id 和 status 的JSON字符串。"
            order_id = data.get("order_id")
            status = data.get("status")
            if not all([order_id, status]):
                return "缺少必要参数：order_id、status"
            current_result = await order_agent.get_order_by_id(order_id)
            if not current_result["success"]:
                return f"无法获取订单当前状态：{current_result['error']}"
            current_status = current_result["data"].get("status")
            valid_transitions = {
                "PENDING_PAYMENT": ["PAID", "CANCELLED"],
                "PAID": ["DELIVERED", "CANCELLED"],
                "DELIVERED": ["FINISHED"]
            }
            if status not in valid_transitions.get(current_status, []):
                return f"无效的状态转换：从 {current_status} 到 {status} 是不允许的。"
            result = await order_agent.update_order_status(order_id, status)
            if result["success"]:
                return f"订单状态更新成功：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"更新订单状态失败：{result['error']}"
        except Exception as e:
            return f"更新订单状态时发生错误：{str(e)}"

    return Tool(
        name="update_order_status",
        func=_update_order_status_sync, # 【修改】提供一个同步函数
        coro=_update_order_status,      # 【修改】同时提供异步函数
        description="更新订单状态。输入必须是包含 order_id 和 status 的JSON字符串。"
    )


def cancel_order_tool(order_agent):
    """取消订单工具"""

    def _cancel_order_sync(order_id: str) -> str:
        """同步包装器"""
        return asyncio.run(_cancel_order(order_id))

    async def _cancel_order(order_id: str) -> str:
        """取消订单"""
        try:
            order_result = await order_agent.get_order_by_id(order_id.strip())
            if not order_result["success"]:
                return f"无法获取订单信息：{order_result['error']}"
            order_data = order_result["data"]
            if order_data.get("status") not in ["PENDING_PAYMENT", "PAID"]:
                return "只能取消状态为“待支付”或“已支付”的订单。"
            result = await order_agent.update_order_status(order_id, "CANCELLED")
            if result["success"]:
                return f"订单取消成功：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"取消订单失败：{result['error']}"
        except Exception as e:
            return f"取消订单时发生错误：{str(e)}"

    return Tool(
        name="cancel_order",
        func=_cancel_order_sync, # 【修改】提供一个同步函数
        coro=_cancel_order,      # 【修改】同时提供异步函数
        description="取消一个订单，参数：订单ID"
    )


# ----------------------------------------------------------------------
# 订单代理主类 (无变化)
# ----------------------------------------------------------------------
class OrderAgent:
    """
    订单代理类 - 负责处理订单相关业务
    集成订单微服务 API
    """
    _agent_executor: Optional[AgentExecutor] = None

    def __init__(self):
        """
        初始化一个无状态的 AgentExecutor。
        记忆将在每次调用时通过 chat_history 参数动态传入。
        """
        self.config = OrderConfig()
        self.logger = logging.getLogger(__name__)
        self.order_api = OrderServiceAPI()
        self.order_status_map = {
            "PENDING_PAYMENT": "待支付", "PAID": "已支付",
            "DELIVERED": "已发货", "FINISHED": "已完成", "CANCELLED": "已取消"
        }

        # 初始化 LLM
        llm = ChatOpenAI(
            api_key=self.config.SILICONFLOW_API_KEY,
            base_url=self.config.SILICONFLOW_BASE_URL,
            model=self.config.MODEL_NAME,
            temperature=self.config.MODEL_TEMPERATURE,
            max_tokens=self.config.MAX_TOKENS,
            timeout=60.0
        )

        # 初始化工具
        tools = self._get_order_tools()

        # Prompt 模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是专业的订单助手。你的核心任务是根据用户的指令和对话历史，调用工具来处理订单。

**工作流程:**
1.  **分析意图**: 仔细分析用户的最新输入和完整的对话历史，理解用户的具体需求（如下单、查单、取消等）。
2.  **提取信息**:
    -   **下单时**: 你必须从对话历史中找到用户想要下单的商品名称和对应的 `product_id`。`GuideAgent` 的推荐报告里包含了 `product_id`。
    -   **用户ID**: 用户的 `user_id` 会在输入中直接提供给你，你必须使用它。
    -   **其他信息**: 根据需要从对话历史或用户输入中提取订单ID、新状态等。
3.  **调用工具**: 使用提取到的信息，以正确的JSON格式调用相应的工具。
    -   `create_order` 工具需要 `user_id` 和 `products` 列表。
4.  **响应用户**: 根据工具的执行结果，生成清晰、友好的回复。

**重要规则:**
-   绝不虚构信息。所有操作都必须基于工具的调用。
-   如果缺少必要信息（例如在对话历史中找不到 `product_id`），必须向用户提问以获取信息。
-   严格遵守订单状态流程：PENDING_PAYMENT -> PAID -> DELIVERED -> FINISHED。CANCELLED 状态可以在 PENDING_PAYMENT 或 PAID 时进入。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "User ID: {user_id}\nUser Request: {input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 创建 agent
        base_agent = create_tool_calling_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )

        # 初始化一个不带 memory 的 AgentExecutor
        self._agent_executor = AgentExecutor(
            agent=base_agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
        )

        print("OrderAgent initialized with a stateless executor and updated prompt.")

    def _get_order_tools(self):
        """获取订单工具列表"""
        return [
            create_order_tool(self),
            get_order_by_id_tool(self),
            get_orders_by_user_tool(self),
            update_order_status_tool(self),
            cancel_order_tool(self)
        ]

    async def process_message(self, user_input: str, session_id: str, user_id: str,
                              chat_history: List[BaseMessage]) -> str:
        """
        处理用户消息，直接使用由监管者传入的全局 chat_history 作为记忆。
        返回一个字符串作为响应。
        """
        self.logger.info(f"--- OrderAgent 正在处理请求 (Session: {session_id}) ---")
        self.logger.info(f"--- 接收到的全局历史记录条数: {len(chat_history)} ---")

        try:
            # 在 ainvoke 中明确传入 user_id，以匹配新的 prompt 模板
            response = await self._agent_executor.ainvoke({
                "input": user_input,
                "user_id": user_id,
                "chat_history": chat_history
            })

            output = response.get("output", "OrderAgent: 抱歉，我无法处理您的请求。")
            self.logger.info(f"OrderAgent 响应: {output}")
            return str(output)

        except Exception as e:
            import traceback
            error_msg = f"OrderAgent 在处理请求时出错: {str(e)}"
            self.logger.error(f"ERROR: {error_msg}\n{traceback.format_exc()}")
            return error_msg

    # ----------------------------------------------------------------------
    # 业务逻辑方法 (无变化)
    # ----------------------------------------------------------------------
    async def create_order(self, user_id: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建新订单"""
        try:
            if not products or not isinstance(products, list):
                return {"success": False, "error": "商品列表不能为空且必须是列表"}
            for product in products:
                if "product_id" not in product or "quantity" not in product:
                    return {"success": False, "error": "每个商品必须包含 product_id 和 quantity 字段"}
                if not isinstance(product["quantity"], int) or product["quantity"] <= 0:
                    return {"success": False, "error": "商品数量必须是大于0的整数"}
            return await self.order_api.create_order(user_id=user_id, products=products)
        except Exception as e:
            self.logger.error(f"创建订单失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_order_by_id(self, order_id: str) -> Dict[str, Any]:
        """根据订单ID获取订单信息"""
        try:
            return await self.order_api.get_order_by_id(order_id)
        except Exception as e:
            self.logger.error(f"获取订单信息失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_orders_by_user(self, user_id: str) -> Dict[str, Any]:
        """获取用户的所有订单"""
        try:
            return await self.order_api.get_orders_by_user(user_id)
        except Exception as e:
            self.logger.error(f"获取用户订单失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """更新订单状态"""
        try:
            valid_statuses = ["PAID", "DELIVERED", "FINISHED", "CANCELLED"]
            if status not in valid_statuses:
                return {"success": False, "error": f"无效的状态值，有效状态: {', '.join(valid_statuses)}"}
            return await self.order_api.update_order_status(order_id, status)
        except Exception as e:
            self.logger.error(f"更新订单状态失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_order_help(self) -> str:
        """获取订单帮助信息"""
        help_text = f"""
        订单代理功能说明：

        核心功能：
        1. 创建新订单
        2. 根据订单ID查询订单详情
        3. 查询用户的订单列表
        4. 更新订单状态
        5. 取消订单

        订单状态流程：
        - PENDING_PAYMENT (待支付) → PAID (已支付) → DELIVERED (已发货) → FINISHED (已完成)
        - 待支付和已支付状态的订单可以取消(CANCELLED)

        数据字段规范：
        - 订单ID: order_id
        - 用户ID: user_id
        - 商品列表: products (格式: [{{"product_id": "商品ID", "quantity": 数量}}])
        - 订单状态: status

        注意：
        - 创建订单需要用户ID和商品列表
        - 状态更新必须遵循状态流程规则
        - 只能取消待支付或已支付的订单
        - 此代理集成了大模型理解能力，能够智能解析用户自然语言输入
        - 与微服务API数据格式完全一致
        """
        return help_text


# ----------------------------------------------------------------------
# 全局 OrderAgent 实例管理 (无变化)
# ----------------------------------------------------------------------
order_agent_instance: Optional['OrderAgent'] = None


async def get_order_agent() -> 'OrderAgent':
    global order_agent_instance
    if order_agent_instance is None:
        order_agent_instance = OrderAgent()
    return order_agent_instance
