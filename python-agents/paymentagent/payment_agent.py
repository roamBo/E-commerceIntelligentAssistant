from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, Optional, List, TypedDict
import json
import logging
import requests
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
    """支付服务 API 封装 - 基于 pay_api.txt 接口文档（排除接口2）"""
    
    def __init__(self, base_url: str = "http://10.172.66.224:8084/payment"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        self.logger = logging.getLogger(__name__)
        
    def create_payment(self, order_id: str, user_id: str, amount: float, status: str = "PENDING") -> Dict[str, Any]:
        """
        接口 1：创建新的支付
        方法：POST
        路径：/api/payments
        """
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
            self.logger.error(f"创建支付失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_all_payments(self) -> Dict[str, Any]:
        """
        接口 3：获取所有支付
        方法：GET
        路径：/api/payments
        """
        url = f"{self.base_url}/api/payments"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取所有支付失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_payment_by_id(self, payment_id: str) -> Dict[str, Any]:
        """
        接口 4：根据 ID 获取支付
        方法：GET
        路径：/api/payments/{id}
        """
        url = f"{self.base_url}/api/payments/{payment_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_payments_by_user(self, user_id: str) -> Dict[str, Any]:
        """
        接口 5：根据用户 ID 获取支付
        方法：GET
        路径：/api/payments/user/{id}
        """
        url = f"{self.base_url}/api/payments/user/{user_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取用户支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_payment(self, payment_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        接口 6：更新支付
        方法：PUT
        路径：/api/payments/{id}
        状态可选值：PENDING, SUCCESS, FAILED
        """
        url = f"{self.base_url}/api/payments/{payment_id}"
        
        try:
            response = self.session.put(url, json=payment_data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"更新支付失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_payment_status(self, payment_id: str, status: str) -> Dict[str, Any]:
        """
        接口 7：更新支付状态
        方法：PATCH
        路径：/api/payments/{id}/status
        """
        url = f"{self.base_url}/api/payments/{payment_id}/status"
        data = {"status": status}
        
        try:
            response = self.session.patch(url, json=data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"更新支付状态失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def delete_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        接口 8：删除支付
        方法：DELETE
        路径：/api/payments/{id}
        """
        url = f"{self.base_url}/api/payments/{payment_id}"
        
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return {"success": True, "data": response.json() if response.content else {}}
        except Exception as e:
            self.logger.error(f"删除支付失败: {str(e)}")
            return {"success": False, "error": str(e)}

class PaymentAgent:
    """
    支付代理类 - 负责处理支付和退款相关业务
    专注于调用支付微服务 API，支付通过微服务模拟进行
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
            
            # 创建支付（微服务模拟）
            result = self.create_payment(
                order_id=order_info.get("order_id"),
                user_id=state["user_id"],
                amount=payment_info.get("amount"),
                payment_method=payment_info.get("payment_method", "simulated")
            )
            
            if result["success"]:
                state["payment_info"].update(result["data"])
                state["agent_response"] = f"支付创建成功，支付ID: {result['data'].get('id', 'N/A')}"
                state["next_action"] = "notify_comm_agent"
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
            
            # 处理退款 - 通过更新支付状态
            result = self.process_refund(
                payment_id=payment_info["payment_id"],
                refund_reason=payment_info.get("refund_reason", "用户申请退款")
            )
            
            if result["success"]:
                state["payment_info"].update(result["data"])
                state["agent_response"] = f"退款申请成功，支付状态已更新"
                state["next_action"] = "notify_comm_agent"
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
                status_text = self.payment_status_map.get(payment_data.get("status", "UNKNOWN"), payment_data.get("status", "UNKNOWN"))
                
                state["agent_response"] = f"支付状态：{status_text}"
                state["payment_info"].update(payment_data)
                state["next_action"] = "notify_comm_agent"
            else:
                state["error_message"] = result["error"]
                state["next_action"] = "handle_query_error"
                
        except Exception as e:
            self.logger.error(f"查询支付状态失败: {str(e)}")
            state["error_message"] = str(e)
            state["next_action"] = "handle_query_error"
            
        return state

    def create_payment(self, order_id: str, user_id: str, amount: float, payment_method: str = "simulated") -> Dict[str, Any]:
        """
        创建支付订单（微服务模拟）
        
        Args:
            order_id: 订单ID
            user_id: 用户ID
            amount: 支付金额
            payment_method: 支付方式（模拟）
            
        Returns:
            Dict[str, Any]: 支付创建结果
        """
        try:
            # 验证支付金额
            if amount <= 0:
                return {"success": False, "error": "支付金额必须大于0"}
            
            if amount > self.config.MAX_PAYMENT_AMOUNT:
                return {"success": False, "error": f"支付金额超过限额 {self.config.MAX_PAYMENT_AMOUNT}"}
            
            # 创建支付订单（微服务模拟）
            payment_result = self.payment_api.create_payment(
                order_id=order_id,
                user_id=user_id,
                amount=amount,
                status="PENDING"
            )
            
            if payment_result["success"]:
                # 添加支付方式信息
                payment_data = payment_result["data"]
                payment_data["payment_method"] = payment_method
                payment_data["payment_type"] = "simulated"
                payment_data["description"] = f"模拟支付 - 订单{order_id}"
                
                self.logger.info(f"创建模拟支付成功: {payment_data.get('id')} - {amount}元")
                
                return {
                    "success": True,
                    "data": payment_data
                }
            else:
                return payment_result
                
        except Exception as e:
            self.logger.error(f"创建支付失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def process_refund(self, payment_id: str, refund_reason: str = "用户申请退款") -> Dict[str, Any]:
        """
        处理退款 - 通过更新支付状态（微服务模拟）
        
        Args:
            payment_id: 支付ID
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
            if payment_data.get("status") not in ["SUCCESS"]:
                return {"success": False, "error": "只有成功的支付才能退款"}
            
            # 更新支付状态为退款中
            refund_result = self.payment_api.update_payment_status(payment_id, "REFUNDING")
            
            if refund_result["success"]:
                self.logger.info(f"退款申请已提交: {payment_id}, 原因: {refund_reason}")
                
                # 模拟退款处理完成（实际应该由微服务异步处理）
                # 这里为了演示，直接更新为已退款状态
                final_result = self.payment_api.update_payment_status(payment_id, "REFUNDED")
                
                return {
                    "success": True,
                    "data": {
                        "payment_id": payment_id,
                        "refund_reason": refund_reason,
                        "status": "REFUNDED",
                        "refund_time": datetime.now().isoformat(),
                        "message": "退款处理完成（模拟）"
                    }
                }
            else:
                return refund_result
                
        except Exception as e:
            self.logger.error(f"处理退款失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def simulate_payment_success(self, payment_id: str) -> Dict[str, Any]:
        """
        模拟支付成功（用于测试）
        
        Args:
            payment_id: 支付ID
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        try:
            result = self.payment_api.update_payment_status(payment_id, "SUCCESS")
            
            if result["success"]:
                self.logger.info(f"模拟支付成功: {payment_id}")
                return {
                    "success": True,
                    "message": f"支付 {payment_id} 模拟成功",
                    "data": result["data"]
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"模拟支付成功失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def simulate_payment_failure(self, payment_id: str) -> Dict[str, Any]:
        """
        模拟支付失败（用于测试）
        
        Args:
            payment_id: 支付ID
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        try:
            result = self.payment_api.update_payment_status(payment_id, "FAILED")
            
            if result["success"]:
                self.logger.info(f"模拟支付失败: {payment_id}")
                return {
                    "success": True,
                    "message": f"支付 {payment_id} 模拟失败",
                    "data": result["data"]
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"模拟支付失败失败: {str(e)}")
            return {"success": False, "error": str(e)}

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
                if not isinstance(payments, list):
                    payments = [payments] if payments else []
                
                formatted_payments = []
                
                for payment in payments:
                    formatted_payment = {
                        "payment_id": payment.get("id"),
                        "order_id": payment.get("orderId"),
                        "amount": payment.get("amount"),
                        "status": self.payment_status_map.get(payment.get("status"), payment.get("status")),
                        "payment_method": payment.get("payment_method", "simulated"),
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

    def delete_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        删除支付记录
        
        Args:
            payment_id: 支付ID
            
        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            result = self.payment_api.delete_payment(payment_id)
            
            if result["success"]:
                self.logger.info(f"支付记录已删除: {payment_id}")
                return {
                    "success": True,
                    "message": f"支付记录 {payment_id} 已成功删除"
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"删除支付记录失败: {str(e)}")
            return {"success": False, "error": str(e)}

    # 为其他 Agent 提供的接口方法
    def handle_inter_agent_request(self, request_type: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理来自其他 Agent 的请求
        
        Args:
            request_type: 请求类型
            request_data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            if request_type == "create_payment":
                return self.create_payment(
                    order_id=request_data.get("order_id"),
                    user_id=request_data.get("user_id"),
                    amount=request_data.get("amount"),
                    payment_method=request_data.get("payment_method", "simulated")
                )
            
            elif request_type == "process_refund":
                return self.process_refund(
                    payment_id=request_data.get("payment_id"),
                    refund_reason=request_data.get("refund_reason", "用户申请退款")
                )
            
            elif request_type == "get_payment_status":
                return self.payment_api.get_payment_by_id(request_data.get("payment_id"))
            
            elif request_type == "get_user_payments":
                return self.get_user_payments(request_data.get("user_id"))
            
            elif request_type == "delete_payment":
                return self.delete_payment(request_data.get("payment_id"))
            
            elif request_type == "simulate_payment_success":
                return self.simulate_payment_success(request_data.get("payment_id"))
            
            elif request_type == "simulate_payment_failure":
                return self.simulate_payment_failure(request_data.get("payment_id"))
            
            else:
                return {"success": False, "error": f"不支持的请求类型: {request_type}"}
                
        except Exception as e:
            self.logger.error(f"处理跨Agent请求失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_payment_help(self) -> str:
        """
        获取支付帮助信息
        
        Returns:
            str: 帮助信息
        """
        help_text = f"""
        支付代理功能说明：
        
        🔧 核心功能：
        1. 💳 创建支付订单（微服务模拟）
        2. 💰 处理退款申请（更新支付状态）
        3. 📊 查询支付状态
        4. 📋 获取用户支付记录
        5. 🗑️ 删除支付记录
        6. 🎭 模拟支付成功/失败（测试用）
        
        🎯 支付方式：模拟支付（不接入真实第三方）
        💱 支持的币种：{', '.join(self.config.SUPPORTED_CURRENCIES)}
        💰 最大支付金额：{self.config.MAX_PAYMENT_AMOUNT}
        
        ⚠️ 注意：
        - 所有支付都是模拟的，不涉及真实资金
        - 支付状态由微服务管理
        - 用户交互由 comm_agent 负责
        """
        return help_text

    # 兼容性方法（保持与现有代码的兼容）
    def process_request(self, user_input: str) -> str:
        """
        处理用户请求（兼容性方法）
        
        Args:
            user_input: 用户输入
            
        Returns:
            str: 处理结果
        """
        return "此功能已迁移至多智能体架构，请通过 comm_agent 访问"