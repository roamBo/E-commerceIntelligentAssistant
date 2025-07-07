from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, Optional, List, TypedDict
import json
import logging
import requests
import hashlib
import time
from datetime import datetime
from config import PaymentConfig

# LangGraph 状态定义（占位框架）
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

class PaymentServiceAPI:
    """支付服务 API 封装"""
    
    def __init__(self, base_url: str = "http://10.172.66.224:8084/payment"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        
    def create_payment(self, order_id: str, user_id: str, amount: float, status: str = "PENDING") -> Dict[str, Any]:
        """创建新的支付"""
        url = f"{self.base_url}/api/payments"
        data = {
            "orderId": order_id,
            "userId": user_id,
            "amount": amount,
            "status": status
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"创建支付失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_alipay_payment(self, out_trade_no: str, total_amount: float, subject: str) -> Dict[str, Any]:
        """创建支付宝支付"""
        url = f"{self.base_url}/api/payments/alipay"
        data = {
            "outTradeNo": out_trade_no,
            "totalAmount": total_amount,
            "subject": subject
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"创建支付宝支付失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_payment_by_id(self, payment_id: str) -> Dict[str, Any]:
        """根据 ID 获取支付"""
        url = f"{self.base_url}/api/payments/{payment_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"获取支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_payments_by_user(self, user_id: str) -> Dict[str, Any]:
        """根据用户 ID 获取支付"""
        url = f"{self.base_url}/api/payments/user/{user_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"获取用户支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_payment_status(self, payment_id: str, status: str) -> Dict[str, Any]:
        """更新支付状态"""
        url = f"{self.base_url}/api/payments/{payment_id}/status"
        data = {"status": status}
        
        try:
            response = self.session.patch(url, json=data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            logging.error(f"更新支付状态失败: {str(e)}")
            return {"success": False, "error": str(e)}

class PaymentAgent:
    """
    支付代理类 - 负责处理支付和退款相关业务
    集成真实的支付服务 API 和第三方支付网关
    """

    def __init__(self, config: PaymentConfig = None):
        """
        初始化支付代理

        Args:
            config: 配置对象，如果不提供则使用默认配置
        """
        self.config = config or PaymentConfig()
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
        self.payment_api = PaymentServiceAPI()
        
        # 支付状态映射
        self.payment_status_map = {
            "PENDING": "待支付",
            "SUCCESS": "支付成功", 
            "FAILED": "支付失败",
            "REFUNDED": "已退款",
            "REFUNDING": "退款中"
        }

    def process_payment_request(self, state: AgentState) -> AgentState:
        """
        处理支付请求（LangGraph 节点函数）
        
        Args:
            state: 当前状态
            
        Returns:
            AgentState: 更新后的状态
        """
        try:
            payment_info = state.get("payment_info", {})
            order_info = state.get("order_info", {})
            
            if not payment_info or not order_info:
                state["error_message"] = "缺少支付或订单信息"
                state["next_action"] = "request_missing_info"
                return state
            
            # 创建支付
            result = self.create_payment(
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

    def process_refund_request(self, state: AgentState) -> AgentState:
        """
        处理退款请求（LangGraph 节点函数）
        
        Args:
            state: 当前状态
            
        Returns:
            AgentState: 更新后的状态
        """
        try:
            payment_info = state.get("payment_info", {})
            
            if not payment_info.get("payment_id"):
                state["error_message"] = "缺少支付ID"
                state["next_action"] = "request_payment_id"
                return state
            
            # 处理退款
            result = self.process_refund(
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

    def check_payment_status(self, state: AgentState) -> AgentState:
        """
        查询支付状态（LangGraph 节点函数）
        
        Args:
            state: 当前状态
            
        Returns:
            AgentState: 更新后的状态
        """
        try:
            payment_info = state.get("payment_info", {})
            payment_id = payment_info.get("payment_id")
            
            if not payment_id:
                state["error_message"] = "缺少支付ID"
                state["next_action"] = "request_payment_id"
                return state
            
            # 查询支付状态
            result = self.payment_api.get_payment_by_id(payment_id)
            
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

    def create_payment(self, order_id: str, user_id: str, amount: float, payment_method: str = "alipay") -> Dict[str, Any]:
        """
        创建支付订单
        
        Args:
            order_id: 订单ID
            user_id: 用户ID
            amount: 支付金额
            payment_method: 支付方式
            
        Returns:
            Dict[str, Any]: 支付创建结果
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
            payment_result = self.payment_api.create_payment(
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
                alipay_result = self.payment_api.create_alipay_payment(
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

    def process_refund(self, payment_id: str, refund_amount: Optional[float] = None, refund_reason: str = "用户申请退款") -> Dict[str, Any]:
        """
        处理退款
        
        Args:
            payment_id: 支付ID
            refund_amount: 退款金额（None表示全额退款）
            refund_reason: 退款原因
            
        Returns:
            Dict[str, Any]: 退款处理结果
        """
        try:
            # 获取原支付信息
            payment_result = self.payment_api.get_payment_by_id(payment_id)
            
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
            status_result = self.payment_api.update_payment_status(payment_id, "REFUNDING")
            
            if not status_result["success"]:
                return status_result
            
            # 这里应该调用真实的第三方支付退款 API
            # 模拟退款处理
            refund_success = self._process_third_party_refund(payment_data, actual_refund_amount, refund_reason)
            
            if refund_success:
                # 更新支付状态为已退款
                self.payment_api.update_payment_status(payment_id, "REFUNDED")
                
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
                self.payment_api.update_payment_status(payment_id, "SUCCESS")
                return {"success": False, "error": "第三方退款处理失败"}
                
        except Exception as e:
            self.logger.error(f"处理退款失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def _process_third_party_refund(self, payment_data: Dict[str, Any], refund_amount: float, refund_reason: str) -> bool:
        """
        处理第三方支付退款（模拟）
        
        Args:
            payment_data: 原支付数据
            refund_amount: 退款金额
            refund_reason: 退款原因
            
        Returns:
            bool: 退款是否成功
        """
        # 这里应该根据不同的支付方式调用相应的第三方退款 API
        # 目前模拟处理
        try:
            # 模拟退款成功
            time.sleep(0.1)  # 模拟网络延迟
            return True
        except Exception as e:
            self.logger.error(f"第三方退款失败: {str(e)}")
            return False

    def handle_payment_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理支付回调
        
        Args:
            callback_data: 回调数据
            
        Returns:
            Dict[str, Any]: 处理结果
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
            result = self.payment_api.update_payment_status(payment_id, status)
            
            if result["success"]:
                self.logger.info(f"支付回调处理成功: {payment_id} -> {status}")
                
                # 通知其他系统（订单系统等）
                self._notify_other_systems(payment_id, status)
                
                return {"success": True, "message": "回调处理成功"}
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"处理支付回调失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def _verify_callback_signature(self, callback_data: Dict[str, Any]) -> bool:
        """
        验证回调签名
        
        Args:
            callback_data: 回调数据
            
        Returns:
            bool: 验证是否成功
        """
        # 这里应该实现真实的签名验证逻辑
        # 目前模拟验证成功
        return True

    def _notify_other_systems(self, payment_id: str, status: str):
        """
        通知其他系统
        
        Args:
            payment_id: 支付ID
            status: 支付状态
        """
        # 这里应该通知订单系统等其他系统
        # 可以通过消息队列、HTTP 请求等方式
        self.logger.info(f"通知其他系统: 支付 {payment_id} 状态更新为 {status}")

    def get_user_payments(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户的支付记录
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 支付记录
        """
        try:
            result = self.payment_api.get_payments_by_user(user_id)
            
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
    def process_request(self, user_input: str) -> str:
        """
        处理用户请求（兼容性方法）
        
        Args:
            user_input: 用户输入
            
        Returns:
            str: 处理结果
        """
        # 这个方法主要用于向后兼容，实际使用中应该通过 LangGraph 调用
        return "此功能已迁移至多智能体架构，请通过 comm_agent 访问"

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