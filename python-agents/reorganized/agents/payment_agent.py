# agents/payment_agent.py
import logging
import asyncio  # 【新增】用于异步包装 requests
import requests  # 【新增】用于同步 HTTP 请求
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, TypedDict
from urllib.parse import urlparse  # 【新增】用于解析 Redis URL

from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage, SystemMessage # 暂时不需要，因为 PaymentAgent 不直接使用 LangChain 记忆
# from langchain_core.prompts import ChatPromptTemplate # 暂时不需要

from config import Config  # 导入 Config


# LangGraph 状态定义（这里只定义 PaymentAgent 内部可能用到的部分，
# 完整的 AgentState 会在 supervisor_agent.py 中定义）
class AgentState(TypedDict):
    """多智能体状态结构"""
    user_id: str
    session_id: str
    current_agent: str
    conversation_history: List[Dict[str, Any]]
    order_info: Optional[Dict[str, Any]]
    payment_info: Optional[Dict[str, Any]]
    user_input: str
    agent_response: str
    error_message: Optional[str]
    next_action: Optional[str]


# ----------------------------------------------------------------------
# 以下是 PaymentAgent 内部的配置和 API 封装，直接放在这里以避免额外的文件依赖
# ----------------------------------------------------------------------
class PaymentConfig:
    """支付代理配置"""
    SILICONFLOW_API_KEY: str = Config.SILICONFLOW_API_KEY
    SILICONFLOW_BASE_URL: str = Config.SILICONFLOW_API_BASE
    MODEL_NAME: str = Config.LLM_MODEL_NAME
    MODEL_TEMPERATURE: float = Config.LLM_TEMPERATURE
    MAX_TOKENS: int = 500

    SUPPORTED_PAYMENT_METHODS: List[str] = ["alipay", "wechat", "unionpay"]
    SUPPORTED_CURRENCIES: List[str] = ["CNY", "USD"]
    MAX_PAYMENT_AMOUNT: float = 10000.0


class PaymentServiceAPI:
    """支付服务 API 封装"""

    def __init__(self, base_url: str = "http://10.172.66.224:8084/payment"):  # 假设这个是外部支付服务的URL
        self.base_url = base_url
        self.session = requests.Session()  # 使用 requests.Session 保持连接
        self.session.timeout = 30

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
            # 使用 asyncio.to_thread 包装同步的 requests 调用
            response = await asyncio.to_thread(self.session.post, url, json=data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"创建支付失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def create_alipay_payment(self, out_trade_no: str, total_amount: float, subject: str) -> Dict[str, Any]:
        """创建支付宝支付"""
        url = f"{self.base_url}/api/payments/alipay"
        data = {
            "outTradeNo": out_trade_no,
            "totalAmount": total_amount,
            "subject": subject
        }

        try:
            response = await asyncio.to_thread(self.session.post, url, json=data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"创建支付宝支付失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_payment_by_id(self, payment_id: str) -> Dict[str, Any]:
        """根据 ID 获取支付"""
        url = f"{self.base_url}/api/payments/{payment_id}"

        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"获取支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_payments_by_user(self, user_id: str) -> Dict[str, Any]:
        """根据用户 ID 获取支付"""
        url = f"{self.base_url}/api/payments/user/{user_id}"

        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"获取用户支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def update_payment_status(self, payment_id: str, status: str) -> Dict[str, Any]:
        """更新支付状态"""
        url = f"{self.base_url}/api/payments/{payment_id}/status"
        data = {"status": status}

        try:
            response = await asyncio.to_thread(self.session.patch, url, json=data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"更新支付状态失败: {str(e)}")
            return {"success": False, "error": str(e)}


# ----------------------------------------------------------------------

class PaymentAgent:
    """
    支付代理类 - 负责处理支付和退款相关业务
    集成真实的支付服务 API 和第三方支付网关
    """

    def __init__(self):  # 移除 config 参数，直接使用 Config
        """
        初始化支付代理
        """
        self.config = PaymentConfig()  # 使用内部 PaymentConfig
        self.logger = logging.getLogger(__name__)

        # 初始化 LLM（仅用于复杂逻辑处理）
        self.llm = ChatOpenAI(
            api_key=self.config.SILICONFLOW_API_KEY,
            base_url=self.config.SILICONFLOW_BASE_URL,
            model=self.config.MODEL_NAME,
            temperature=self.config.MODEL_TEMPERATURE,
            max_tokens=self.config.MAX_TOKENS,
            timeout=30
        )

        # 初始化支付服务 API
        self.payment_api = PaymentServiceAPI()  # 假设 PaymentServiceAPI 的 base_url 是固定的

        # 支付状态映射
        self.payment_status_map = {
            "PENDING": "待支付",
            "SUCCESS": "支付成功",
            "FAILED": "支付失败",
            "REFUNDED": "已退款",
            "REFUNDING": "退款中"
        }
        print("PaymentAgent initialized.")

    async def process_message(self, user_input: str, session_id: str) -> str:
        """
        处理用户消息并返回 Agent 的响应。
        注意：PaymentAgent 原本没有 LangChain AgentExecutor 结构，
        这里为了兼容 LangGraph 节点，直接返回一个模拟响应。
        如果 PaymentAgent 内部也需要 LLM 驱动的复杂逻辑，
        则需要像 GuideAgent 或 OrderAgent 那样构建 AgentExecutor。
        """
        self.logger.info(f"PaymentAgent 收到消息: {user_input} (Session: {session_id})")
        # 这里可以根据 user_input 简单判断意图并调用内部方法
        # 例如：
        if "支付" in user_input and "创建" in user_input:
            # 假设从 user_input 中解析出 order_id, user_id, amount
            # 这部分通常由 LLM 或更复杂的解析器完成
            # 为了演示，我们直接返回一个模拟结果
            return "PaymentAgent: 收到创建支付请求，但需要更多信息（如订单ID、金额）。"
        elif "退款" in user_input:
            return "PaymentAgent: 收到退款请求，但需要支付ID和退款金额。"
        elif "状态" in user_input and "支付" in user_input:
            return "PaymentAgent: 收到查询支付状态请求，但需要支付ID。"
        else:
            return "PaymentAgent: 我是支付助手，请问您有什么支付或退款相关的问题？"

    # 以下是 PaymentAgent 原有的业务逻辑方法，供 LangGraph 节点或内部调用
    async def process_payment_request(self, state: AgentState) -> AgentState:
        """
        处理支付请求（LangGraph 节点函数）
        """
        try:
            payment_info = state.get("payment_info", {})
            order_info = state.get("order_info", {})

            if not payment_info or not order_info:
                state["error_message"] = "缺少支付或订单信息"
                state["next_action"] = "request_missing_info"
                return state

            # 创建支付
            result = await self.create_payment(
                order_id=order_info.get("order_id"),
                user_id=state["user_id"],
                amount=payment_info.get("amount"),
                payment_method=payment_info.get("payment_method", "alipay")
            )

            if result["success"]:
                state["payment_info"].update(result["data"])
                state["agent_response"] = f"支付创建成功，支付ID: {result['data']['payment_id']}"
                state["next_action"] = "notify_order_agent"
            else:
                state["error_message"] = result["error"]
                state["next_action"] = "handle_payment_error"

        except Exception as e:
            self.logger.error(f"处理支付请求失败: {str(e)}")
            state["error_message"] = str(e)
            state["next_action"] = "handle_payment_error"

        return state

    async def process_refund_request(self, state: AgentState) -> AgentState:
        """
        处理退款请求（LangGraph 节点函数）
        """
        try:
            payment_info = state.get("payment_info", {})

            if not payment_info.get("payment_id"):
                state["error_message"] = "缺少支付ID"
                state["next_action"] = "request_payment_id"
                return state

            # 处理退款
            result = await self.process_refund(
                payment_id=payment_info["payment_id"],
                refund_amount=payment_info.get("refund_amount"),
                refund_reason=payment_info.get("refund_reason", "用户申请退款")
            )

            if result["success"]:
                state["payment_info"].update(result["data"])
                state["agent_response"] = f"退款申请成功，退款ID: {result['data']['refund_id']}"
                state["next_action"] = "notify_order_agent"
            else:
                state["error_message"] = result["error"]
                state["next_action"] = "handle_refund_error"

        except Exception as e:
            self.logger.error(f"处理退款请求失败: {str(e)}")
            state["error_message"] = str(e)
            state["next_action"] = "handle_refund_error"

        return state

    async def check_payment_status(self, state: AgentState) -> AgentState:
        """
        查询支付状态（LangGraph 节点函数）
        """
        try:
            payment_info = state.get("payment_info", {})
            payment_id = payment_info.get("payment_id")

            if not payment_id:
                state["error_message"] = "缺少支付ID"
                state["next_action"] = "request_payment_id"
                return state

            # 查询支付状态
            result = await self.payment_api.get_payment_by_id(payment_id)

            if result["success"]:
                payment_data = result["data"]
                status_text = self.payment_status_map.get(payment_data["status"], payment_data["status"])

                state["agent_response"] = f"支付状态：{status_text}"
                state["payment_info"].update(payment_data)
                state["next_action"] = "return_to_comm_agent"
            else:
                state["error_message"] = result["error"]
                state["next_action"] = "handle_query_error"

        except Exception as e:
            self.logger.error(f"查询支付状态失败: {str(e)}")
            state["error_message"] = str(e)
            state["next_action"] = "handle_query_error"

        return state

    async def create_payment(self, order_id: str, user_id: str, amount: float, payment_method: str = "alipay") -> Dict[
        str, Any]:
        """
        创建支付订单
        """
        try:
            # 验证支付金额
            if amount <= 0:
                return {"success": False, "error": "支付金额必须大于0"}

            if amount > self.config.MAX_PAYMENT_AMOUNT:
                return {"success": False, "error": f"支付金额超过限额 {self.config.MAX_PAYMENT_AMOUNT}"}

            # 验证支付方式
            if payment_method not in self.config.SUPPORTED_PAYMENT_METHODS:
                return {"success": False, "error": f"不支持的支付方式: {payment_method}"}

            # 创建支付订单
            payment_result = await self.payment_api.create_payment(
                order_id=order_id,
                user_id=user_id,
                amount=amount,
                status="PENDING"
            )

            if not payment_result["success"]:
                return payment_result

            payment_id = payment_result["data"].get("id")

            # 根据支付方式创建具体的支付
            if payment_method == "alipay":
                out_trade_no = f"PAY_{payment_id}_{int(time.time())}"
                alipay_result = await self.payment_api.create_alipay_payment(
                    out_trade_no=out_trade_no,
                    total_amount=amount,
                    subject=f"订单支付-{order_id}"
                )

                if alipay_result["success"]:
                    return {
                        "success": True,
                        "data": {
                            "payment_id": payment_id,
                            "out_trade_no": out_trade_no,
                            "payment_url": alipay_result["data"].get("payment_url"),
                            "qr_code": alipay_result["data"].get("qr_code"),
                            "amount": amount,
                            "status": "PENDING"
                        }
                    }
                else:
                    return alipay_result
            else:
                # 其他支付方式的处理逻辑
                return {
                    "success": True,
                    "data": {
                        "payment_id": payment_id,
                        "amount": amount,
                        "status": "PENDING",
                        "payment_method": payment_method
                    }
                }

        except Exception as e:
            self.logger.error(f"创建支付失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_refund(self, payment_id: str, refund_amount: Optional[float] = None,
                             refund_reason: str = "用户申请退款") -> Dict[str, Any]:
        """
        处理退款
        """
        try:
            # 获取原支付信息
            payment_result = await self.payment_api.get_payment_by_id(payment_id)

            if not payment_result["success"]:
                return payment_result

            payment_data = payment_result["data"]

            # 验证支付状态
            if payment_data["status"] not in ["SUCCESS"]:
                return {"success": False, "error": "只有成功的支付才能退款"}

            # 确定退款金额
            original_amount = float(payment_data["amount"])
            actual_refund_amount = refund_amount if refund_amount is not None else original_amount

            if actual_refund_amount <= 0 or actual_refund_amount > original_amount:
                return {"success": False, "error": "退款金额无效"}

            # 生成退款ID
            refund_id = f"REF_{payment_id}_{int(time.time())}"

            # 更新支付状态为退款中
            status_result = await self.payment_api.update_payment_status(payment_id, "REFUNDING")

            if not status_result["success"]:
                return status_result

            # 这里应该调用真实的第三方支付退款 API
            # 模拟退款处理
            refund_success = await self._process_third_party_refund(payment_data, actual_refund_amount, refund_reason)

            if refund_success:
                # 更新支付状态为已退款
                await self.payment_api.update_payment_status(payment_id, "REFUNDED")

                return {
                    "success": True,
                    "data": {
                        "refund_id": refund_id,
                        "payment_id": payment_id,
                        "refund_amount": actual_refund_amount,
                        "refund_reason": refund_reason,
                        "status": "REFUNDED",
                        "refund_time": datetime.now().isoformat()
                    }
                }
            else:
                # 退款失败，恢复支付状态
                await self.payment_api.update_payment_status(payment_id, "SUCCESS")
                return {"success": False, "error": "第三方退款处理失败"}

        except Exception as e:
            self.logger.error(f"处理退款失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _process_third_party_refund(self, payment_data: Dict[str, Any], refund_amount: float,
                                          refund_reason: str) -> bool:
        """
        处理第三方支付退款（模拟）
        """
        # 这里应该根据不同的支付方式调用相应的第三方退款 API
        # 目前模拟处理
        try:
            # 模拟退款成功
            await asyncio.sleep(0.1)  # 模拟网络延迟
            return True
        except Exception as e:
            self.logger.error(f"第三方退款失败: {str(e)}")
            return False

    async def handle_payment_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理支付回调
        """
        try:
            # 验证回调数据
            if not self._verify_callback_signature(callback_data):
                return {"success": False, "error": "回调验证失败"}

            payment_id = callback_data.get("payment_id")
            status = callback_data.get("status")

            if not payment_id or not status:
                return {"success": False, "error": "回调数据不完整"}

            # 更新支付状态
            result = await self.payment_api.update_payment_status(payment_id, status)

            if result["success"]:
                self.logger.info(f"支付回调处理成功: {payment_id} -> {status}")

                # 通知其他系统（订单系统等）
                await self._notify_other_systems(payment_id, status)

                return {"success": True, "message": "回调处理成功"}
            else:
                return result

        except Exception as e:
            self.logger.error(f"处理支付回调失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _verify_callback_signature(self, callback_data: Dict[str, Any]) -> bool:
        """
        验证回调签名
        """
        # 这里应该实现真实的签名验证逻辑
        # 目前模拟验证成功
        return True

    async def _notify_other_systems(self, payment_id: str, status: str):
        """
        通知其他系统
        """
        # 这里应该通知订单系统等其他系统
        # 可以通过消息队列、HTTP 请求等方式
        self.logger.info(f"通知其他系统: 支付 {payment_id} 状态更新为 {status}")

    async def get_user_payments(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户的支付记录
        """
        try:
            result = await self.payment_api.get_payments_by_user(user_id)

            if result["success"]:
                # 格式化支付记录
                payments = result["data"]
                formatted_payments = []

                for payment in payments:
                    formatted_payment = {
                        "payment_id": payment["id"],
                        "order_id": payment["orderId"],
                        "amount": payment["amount"],
                        "status": self.payment_status_map.get(payment["status"], payment["status"]),
                        "create_time": payment.get("createTime", ""),
                        "update_time": payment.get("updateTime", "")
                    }
                    formatted_payments.append(formatted_payment)

                return {
                    "success": True,
                    "data": formatted_payments
                }
            else:
                return result

        except Exception as e:
            self.logger.error(f"获取用户支付记录失败: {str(e)}")
            return {"success": False, "error": str(e)}

    # 兼容性方法（保持与现有代码的兼容）
    async def process_request(self, user_input: str) -> str:
        """
        处理用户请求（兼容性方法）

        Args:
            user_input: 用户输入

        Returns:
            str: 处理结果
        """
        # 这个方法主要用于向后兼容，实际使用中应该通过 LangGraph 调用
        # 为了演示，这里简单地将用户输入传递给 process_message
        return await self.process_message(user_input, "compatibility_session")

    def get_payment_help(self) -> str:
        """
        获取支付帮助信息

        Returns:
            str: 帮助信息
        """
        help_text = f"""
        支付代理功能说明：

        🔧 核心功能：
        1. 💳 创建支付订单
        2. 💰 处理退款申请
        3. 📊 查询支付状态
        4. 🔔 处理支付回调

        📋 支持的支付方式：{', '.join(self.config.SUPPORTED_PAYMENT_METHODS)}
        💱 支持的币种：{', '.join(self.config.SUPPORTED_CURRENCIES)}
        💰 最大支付金额：{self.config.MAX_PAYMENT_AMOUNT}

        ⚠️ 注意：此代理仅处理支付相关逻辑，用户交互由 comm_agent 负责
        """
        return help_text


# 全局 PaymentAgent 实例
payment_agent_instance: Optional['PaymentAgent'] = None


async def get_payment_agent() -> 'PaymentAgent':
    global payment_agent_instance
    if payment_agent_instance is None:
        payment_agent_instance = PaymentAgent()
    return payment_agent_instance
