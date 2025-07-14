# agents/payment_agent.py
import logging
import asyncio
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent, Tool

from config import Config
from models import AgentState


# ----------------------------------------------------------------------
# 支付代理配置
# ----------------------------------------------------------------------
class PaymentConfig:
    """支付代理配置"""
    SILICONFLOW_API_KEY: str = Config.SILICONFLOW_API_KEY
    SILICONFLOW_BASE_URL: str = Config.SILICONFLOW_API_BASE
    MODEL_NAME: str = Config.LLM_MODEL_NAME
    MODEL_TEMPERATURE: float = Config.LLM_TEMPERATURE
    MAX_TOKENS: int = 500
    SUPPORTED_PAYMENT_METHODS: List[str] = ["simulated"]
    SUPPORTED_CURRENCIES: List[str] = ["CNY"]
    MAX_PAYMENT_AMOUNT: float = 10000.0
    DEFAULT_PAYMENT_METHOD: str = "simulated"
    DEFAULT_CURRENCY: str = "CNY"

# ----------------------------------------------------------------------
# 支付服务 API 封装
# ----------------------------------------------------------------------
class PaymentServiceAPI:
    """支付服务 API 封装"""

    def __init__(self, base_url: str = "http://10.172.66.224:8084/payment"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 120
        self.logger = logging.getLogger(__name__)

    async def create_payment(self, order_id: str, user_id: str, amount: float, status: str = "PENDING") -> Dict[
        str, Any]:
        """创建新的支付"""
        url = f"{self.base_url}/api/payments"
        data = {
            "orderId": order_id,
            "userId": user_id,
            "amount": amount,
            "status": status
        }
        try:
            response = await asyncio.to_thread(self.session.post, url, json=data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"创建支付失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_payment_by_id(self, payment_id: str) -> Dict[str, Any]:
        """根据 ID 获取支付"""
        url = f"{self.base_url}/api/payments/{payment_id}"
        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_payments_by_order(self, order_id: str) -> Dict[str, Any]:
        """根据订单 ID 获取支付记录"""
        url = f"{self.base_url}/api/payments/order/{order_id}"
        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取订单支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_payments_by_user(self, user_id: str) -> Dict[str, Any]:
        """根据用户 ID 获取支付"""
        url = f"{self.base_url}/api/payments/user/{user_id}"
        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取用户支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def update_payment_status(self, payment_id: str, status: str) -> Dict[str, Any]:
        """更新支付状态"""
        url = f"{self.base_url}/api/payments/{payment_id}/{status}"
        try:
            response = await asyncio.to_thread(self.session.patch, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"更新支付状态失败: {str(e)}")
            return {"success": False, "error": str(e)}


# ----------------------------------------------------------------------
# 支付代理工具函数
# ----------------------------------------------------------------------
def create_payment_tool(payment_agent):
    """创建支付订单工具"""

    def _create_payment_sync(payment_data: str) -> str:
        return asyncio.run(_create_payment(payment_data))

    async def _create_payment(payment_data: str) -> str:
        try:
            try:
                data = json.loads(payment_data)
            except json.JSONDecodeError:
                return "参数格式错误。输入必须是包含 order_id, user_id, 和 amount 的JSON字符串。"
            order_id = data.get("order_id")
            user_id = data.get("user_id")
            amount = data.get("amount")
            if not all([order_id, user_id, amount]):
                return "缺少必要参数：order_id、user_id、amount"
            try:
                amount = float(amount)
            except (ValueError, TypeError):
                return "金额必须是数字"
            result = await payment_agent.create_payment(order_id, user_id, amount)
            if result["success"]:
                return f"支付创建成功：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"支付创建失败：{result['error']}"
        except Exception as e:
            return f"创建支付时发生错误：{str(e)}"

    return Tool(
        name="create_payment_order",
        func=_create_payment_sync,
        coro=_create_payment,
        description="创建支付订单。输入必须是包含 order_id, user_id, 和 amount 的JSON字符串。"
    )


def query_payment_status_tool(payment_agent):
    """查询支付状态工具"""

    def _query_payment_status_sync(query_data: str) -> str:
        return asyncio.run(_query_payment_status(query_data))

    async def _query_payment_status(query_data: str) -> str:
        try:
            try:
                data = json.loads(query_data)
                payment_id = data.get("payment_id") or data.get("id")
                order_id = data.get("order_id")
            except json.JSONDecodeError:
                payment_id = query_data.strip()
                order_id = None

            if payment_id:
                result = await payment_agent.payment_api.get_payment_by_id(payment_id)
                if result["success"]:
                    payment_data = result["data"]
                    status_text = payment_agent.payment_status_map.get(payment_data.get("status", "UNKNOWN"),
                                                                       payment_data.get("status", "UNKNOWN"))
                    return f"支付状态：{status_text}，详细信息：{json.dumps(payment_data, ensure_ascii=False)}"
                else:
                    return f"查询支付状态失败：{result['error']}"
            elif order_id:
                result = await payment_agent.payment_api.get_payments_by_order(order_id)
                if result["success"]:
                    payments = result["data"]
                    if payments:
                        payment_data = payments[0]
                        status_text = payment_agent.payment_status_map.get(payment_data.get("status", "UNKNOWN"),
                                                                           payment_data.get("status", "UNKNOWN"))
                        return f"订单 {order_id} 的支付状态：{status_text}，详细信息：{json.dumps(payment_data, ensure_ascii=False)}"
                    else:
                        return f"订单 {order_id} 没有找到支付记录"
                else:
                    return f"查询订单支付状态失败：{result['error']}"
            else:
                return "请提供支付ID或订单ID。"
        except Exception as e:
            return f"查询支付状态时发生错误：{str(e)}"

    return Tool(
        name="query_payment_status",
        func=_query_payment_status_sync,
        coro=_query_payment_status,
        description="查询支付状态，参数可以是支付ID，也可以是包含 id 或 order_id 的JSON字符串。"
    )


def process_refund_tool(payment_agent):
    """处理退款工具"""

    def _process_refund_sync(refund_data: str) -> str:
        return asyncio.run(_process_refund(refund_data))

    async def _process_refund(refund_data: str) -> str:
        try:
            try:
                data = json.loads(refund_data)
            except json.JSONDecodeError:
                data = {"id": refund_data.strip()}

            payment_id = data.get("payment_id") or data.get("id")
            if not payment_id:
                return "缺少必要参数：id（支付ID）"

            refund_reason = data.get("reason", "用户申请退款").strip()
            result = await payment_agent.process_refund(payment_id, refund_reason)

            if result["success"]:
                return f"退款处理成功：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"退款处理失败：{result['error']}"
        except Exception as e:
            return f"处理退款时发生错误：{str(e)}"

    return Tool(
        name="process_refund",
        func=_process_refund_sync,
        coro=_process_refund,
        description="处理退款。输入必须是包含 id (支付ID) 的JSON字符串，reason (退款原因)可选。"
    )


def get_user_payments_tool(payment_agent):
    """获取用户支付记录工具"""

    def _get_user_payments_sync(user_id: str) -> str:
        return asyncio.run(_get_user_payments(user_id))

    async def _get_user_payments(user_id: str) -> str:
        try:
            result = await payment_agent.get_user_payments(user_id.strip())
            if result["success"]:
                return f"用户支付记录：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"获取用户支付记录失败：{result['error']}"
        except Exception as e:
            return f"获取用户支付记录时发生错误：{str(e)}"

    return Tool(
        name="get_user_payments",
        func=_get_user_payments_sync,
        coro=_get_user_payments,
        description="获取指定用户的所有支付记录，参数：用户ID"
    )


def get_order_payments_tool(payment_agent):
    """获取订单支付记录工具"""

    def _get_order_payments_sync(order_id: str) -> str:
        return asyncio.run(_get_order_payments(order_id))

    async def _get_order_payments(order_id: str) -> str:
        try:
            result = await payment_agent.payment_api.get_payments_by_order(order_id.strip())
            if result["success"]:
                return f"订单支付记录：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"获取订单支付记录失败：{result['error']}"
        except Exception as e:
            return f"获取订单支付记录时发生错误：{str(e)}"

    return Tool(
        name="get_order_payments",
        func=_get_order_payments_sync,
        coro=_get_order_payments,
        description="获取指定订单的所有支付记录，参数：订单ID"
    )


# ----------------------------------------------------------------------
# 支付代理主类
# ----------------------------------------------------------------------
class PaymentAgent:
    """
    支付代理类 - 负责处理支付和退款相关业务
    """
    _agent_executor: Optional[AgentExecutor] = None

    def __init__(self):
        """
        在 __init__ 中创建一个单一的、不带 memory 的 AgentExecutor 实例。
        """
        self.config = PaymentConfig()
        self.logger = logging.getLogger(__name__)
        self.payment_api = PaymentServiceAPI()
        self.payment_status_map = {
            "PENDING": "待支付", "SUCCESS": "支付成功", "FAILED": "支付失败",
            "REFUNDED": "已退款", "REFUNDING": "退款中"
        }

        llm = ChatOpenAI(
            api_key=self.config.SILICONFLOW_API_KEY,
            base_url=self.config.SILICONFLOW_BASE_URL,
            model=self.config.MODEL_NAME,
            temperature=self.config.MODEL_TEMPERATURE,
            max_tokens=self.config.MAX_TOKENS,
            timeout=60.0
        )

        tools = self._get_payment_tools()

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是专业的支付助手。你的核心任务是根据用户的指令和对话历史，调用工具来处理支付相关业务。

**工作流程:**
1.  **分析意图**: 仔细分析用户的最新输入和完整的对话历史，理解用户的具体需求（如支付订单、查询状态、退款等）。
2.  **主动提取信息**:
    -   **支付订单时**: 如果用户说“支付这个订单”或类似的话，你**必须**首先回顾对话历史，找到之前 `OrderAgent` 创建订单后返回的**订单ID (orderId 或 id)** 和**订单金额 (price 或 amount)**。
    -   **用户ID**: 用户的 `user_id` 会在输入中直接提供给你，你必须使用它。
    -   **其他信息**: 根据需要从对话历史或用户输入中提取支付ID等。
3.  **调用工具**: 在信息齐全后，调用相应的工具。`create_payment_order` 工具需要 `order_id`, `user_id`, 和 `amount`。
4.  **信息不足时提问**: 只有在回顾了整个对话历史后，仍然找不到必要信息（如订单ID），你才应该向用户提问。
5.  **响应用户**: 根据工具的执行结果，生成清晰、专业的回复。

**重要规则:**
-   **首要原则是回顾历史，而不是直接提问。**
-   支付是模拟的，创建后会自动成功。
-   退款需要支付ID。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "User ID: {user_id}\nUser Request: {input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

        self._agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
        print("PaymentAgent initialized with a stateless executor and updated prompt.")

    def _get_payment_tools(self):
        """获取支付工具列表"""
        return [
            create_payment_tool(self),
            query_payment_status_tool(self),
            process_refund_tool(self),
            get_user_payments_tool(self),
            get_order_payments_tool(self)
        ]

    async def process_message(self, user_input: str, session_id: str, user_id: str,
                              chat_history: List[BaseMessage]) -> str:
        """
        处理用户消息，使用传入的全局 chat_history 作为记忆。
        """
        self.logger.info(f"PaymentAgent 收到消息: {user_input} (Session: {session_id})")
        self.logger.info(f"--- 接收到的全局历史记录条数: {len(chat_history)} ---")

        try:
            response = await self._agent_executor.ainvoke({
                "input": user_input,
                "user_id": user_id,
                "chat_history": chat_history
            })

            output = response.get("output", "PaymentAgent: 抱歉，我无法处理您的请求。")
            self.logger.info(f"PaymentAgent 响应: {output}")
            return str(output)

        except Exception as e:
            import traceback
            self.logger.error(f"PaymentAgent 处理消息失败: {str(e)}\n{traceback.format_exc()}")
            return f"PaymentAgent: 抱歉，处理您的请求时发生错误：{str(e)}"

    # ----------------------------------------------------------------------
    # 业务逻辑方法
    # ----------------------------------------------------------------------
    async def create_payment(self, order_id: str, user_id: str, amount: float) -> Dict[str, Any]:
        """创建支付订单（简化版，自动成功）"""
        try:
            if amount <= 0:
                return {"success": False, "error": "支付金额必须大于0"}
            if amount > self.config.MAX_PAYMENT_AMOUNT:
                return {"success": False, "error": f"支付金额超过限额 {self.config.MAX_PAYMENT_AMOUNT}"}

            payment_result = await self.payment_api.create_payment(
                order_id=order_id,
                user_id=user_id,
                amount=amount,
                status="PENDING"
            )
            if not payment_result["success"]:
                return payment_result

            payment_id = payment_result["data"].get("id")
            success_result = await self.payment_api.update_payment_status(payment_id, "SUCCESS")

            if success_result["success"]:
                final_payment_data = success_result["data"].copy()
                final_payment_data.update({
                    "payment_time": datetime.now().isoformat(),
                    "message": "模拟支付已完成"
                })
                self.logger.info(f"模拟支付成功创建并完成: {payment_id} - {amount} CNY")
                return {"success": True, "data": final_payment_data}
            else:
                self.logger.warning(f"支付创建成功但状态更新失败: {payment_id}")
                original_data = payment_result["data"].copy()
                original_data.update({"warning": "支付已创建但状态更新失败，请稍后查询状态"})
                return {"success": True, "data": original_data}
        except Exception as e:
            self.logger.error(f"创建支付失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_refund(self, payment_id: str, refund_reason: str = "用户申请退款") -> Dict[str, Any]:
        """处理退款"""
        try:
            payment_result = await self.payment_api.get_payment_by_id(payment_id)
            if not payment_result["success"]:
                return payment_result
            payment_data = payment_result["data"]
            if payment_data.get("status") not in ["SUCCESS"]:
                return {"success": False, "error": "只有成功的支付才能退款"}

            refund_result = await self.payment_api.update_payment_status(payment_id, "REFUNDING")
            if refund_result["success"]:
                self.logger.info(f"退款申请已提交: {payment_id}, 原因: {refund_reason}")
                final_result = await self.payment_api.update_payment_status(payment_id, "REFUNDED")
                return {
                    "success": True,
                    "data": {
                        "id": payment_id,
                        "refund_reason": refund_reason,
                        "status": "REFUNDED",
                        "refund_time": datetime.now().isoformat(),
                        "message": "退款处理完成"
                    }
                }
            else:
                return refund_result
        except Exception as e:
            self.logger.error(f"处理退款失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_user_payments(self, user_id: str) -> Dict[str, Any]:
        """获取用户的支付记录"""
        try:
            result = await self.payment_api.get_payments_by_user(user_id)
            if result["success"]:
                payments = result["data"]
                if not isinstance(payments, list):
                    payments = [payments] if payments else []

                formatted_payments = []
                for payment in payments:
                    formatted_payment = {
                        "id": payment.get("id"),
                        "orderId": payment.get("orderId"),
                        "userId": payment.get("userId"),
                        "amount": payment.get("amount"),
                        "status": self.payment_status_map.get(payment.get("status"), payment.get("status")),
                        "createAt": payment.get("createAt", ""),
                        "updateAt": payment.get("updateAt", "")
                    }
                    formatted_payments.append(formatted_payment)
                return {"success": True, "data": formatted_payments}
            else:
                return result
        except Exception as e:
            self.logger.error(f"获取用户支付记录失败: {str(e)}")
            return {"success": False, "error": str(e)}


# ----------------------------------------------------------------------
# 全局 PaymentAgent 实例管理
# ----------------------------------------------------------------------
payment_agent_instance: Optional['PaymentAgent'] = None


async def get_payment_agent() -> 'PaymentAgent':
    global payment_agent_instance
    if payment_agent_instance is None:
        payment_agent_instance = PaymentAgent()
    return payment_agent_instance
