# agents/payment_agent.py
import logging
import asyncio
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent, Tool

# 【修改】移除了 ConversationBufferWindowMemory 和 RedisChatMessageHistory
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

    # 简化配置：只支持模拟支付和CNY
    SUPPORTED_PAYMENT_METHODS: List[str] = ["simulated"]
    SUPPORTED_CURRENCIES: List[str] = ["CNY"]
    MAX_PAYMENT_AMOUNT: float = 10000.0
    DEFAULT_PAYMENT_METHOD: str = "simulated"
    DEFAULT_CURRENCY: str = "CNY"


# ----------------------------------------------------------------------
# 支付服务 API 封装（完整版本）
# ----------------------------------------------------------------------
class PaymentServiceAPI:
    """支付服务 API 封装"""

    def __init__(self, base_url: str = "http://10.172.66.224:8084/payment"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        self.logger = logging.getLogger(__name__)

    async def create_payment(self, order_id: str, user_id: str, amount: float, status: str = "PENDING") -> Dict[str, Any]:
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

    async def get_all_payments(self) -> Dict[str, Any]:
        """获取所有支付"""
        url = f"{self.base_url}/api/payments"
        
        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"获取所有支付失败: {str(e)}")
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

# TODO: 不确定是否有用，有用的话应该让微服务增加一个api
    async def get_payments_by_order(self, order_id: str) -> Dict[str, Any]:
        """根据订单 ID 获取支付记录"""
        url = f"{self.base_url}/api/payments"
        
        try:
            response = await asyncio.to_thread(self.session.get, url)
            response.raise_for_status()
            all_payments = response.json()
            
            # 过滤出指定订单的支付记录
            if isinstance(all_payments, list):
                order_payments = [p for p in all_payments if p.get("orderId") == order_id]
            else:
                order_payments = [all_payments] if all_payments.get("orderId") == order_id else []
            
            return {"success": True, "data": order_payments}
        except Exception as e:
            self.logger.error(f"获取订单支付信息失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def update_payment(self, payment_id: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新支付"""
        url = f"{self.base_url}/api/payments/{payment_id}"
        
        try:
            response = await asyncio.to_thread(self.session.put, url, json=payment_data)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"更新支付失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def update_payment_status(self, payment_id: str, status: str) -> Dict[str, Any]:
        """更新支付状态"""
        url = f"{self.base_url}/api/payments/{payment_id}/status"
        
        try:
            response = await asyncio.to_thread(self.session.patch, url, json=status)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            self.logger.error(f"更新支付状态失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def delete_payment(self, payment_id: str) -> Dict[str, Any]:
        """删除支付"""
        url = f"{self.base_url}/api/payments/{payment_id}"
        
        try:
            response = await asyncio.to_thread(self.session.delete, url)
            response.raise_for_status()
            return {"success": True, "data": response.json() if response.content else {}}
        except Exception as e:
            self.logger.error(f"删除支付失败: {str(e)}")
            return {"success": False, "error": str(e)}


# ----------------------------------------------------------------------
# 支付代理工具函数
# ----------------------------------------------------------------------
def create_payment_tool(payment_agent):
    """创建支付订单工具"""
    async def _create_payment(payment_data: str) -> str:
        """创建支付订单，参数为JSON格式字符串"""
        try:
            # 解析JSON参数
            try:
                data = json.loads(payment_data)
            except json.JSONDecodeError:
                return "参数格式错误，请使用JSON格式：{\"order_id\": \"订单ID\", \"user_id\": \"用户ID\", \"amount\": 金额}"
            
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
        func=_create_payment,
        description="创建支付订单，参数为JSON格式：{\"order_id\": \"订单ID\", \"user_id\": \"用户ID\", \"amount\": 金额}"
    )


def query_payment_status_tool(payment_agent):
    """查询支付状态工具"""
    async def _query_payment_status(query_data: str) -> str:
        """查询支付状态，支持通过支付ID或订单ID查询"""
        try:
            # 尝试解析JSON，如果失败则当作简单的ID处理
            try:
                data = json.loads(query_data)
                payment_id = data.get("payment_id") or data.get("id")  # 兼容两种格式
                order_id = data.get("order_id")
            except json.JSONDecodeError:
                # 如果不是JSON，当作支付ID处理
                payment_id = query_data.strip()
                order_id = None
            
            if payment_id:
                # 通过支付ID查询
                result = await payment_agent.payment_api.get_payment_by_id(payment_id)
                
                if result["success"]:
                    payment_data = result["data"]
                    status_text = payment_agent.payment_status_map.get(
                        payment_data.get("status", "UNKNOWN"), 
                        payment_data.get("status", "UNKNOWN")
                    )
                    return f"支付状态：{status_text}，详细信息：{json.dumps(payment_data, ensure_ascii=False)}"
                else:
                    return f"查询支付状态失败：{result['error']}"
            
            elif order_id:
                # 通过订单ID查询
                result = await payment_agent.payment_api.get_payments_by_order(order_id)
                
                if result["success"]:
                    payments = result["data"]
                    if payments:
                        payment_data = payments[0]  # 取第一个支付记录
                        status_text = payment_agent.payment_status_map.get(
                            payment_data.get("status", "UNKNOWN"), 
                            payment_data.get("status", "UNKNOWN")
                        )
                        return f"订单 {order_id} 的支付状态：{status_text}，详细信息：{json.dumps(payment_data, ensure_ascii=False)}"
                    else:
                        return f"订单 {order_id} 没有找到支付记录"
                else:
                    return f"查询订单支付状态失败：{result['error']}"
            
            else:
                return "请提供支付ID或订单ID。格式：支付ID 或 {\"id\": \"支付ID\"} 或 {\"order_id\": \"订单ID\"}"
                
        except Exception as e:
            return f"查询支付状态时发生错误：{str(e)}"
    
    return Tool(
        name="query_payment_status",
        func=_query_payment_status,
        description="查询支付状态，参数：支付ID 或 JSON格式：{\"id\": \"支付ID\"} 或 {\"order_id\": \"订单ID\"}"
    )


def process_refund_tool(payment_agent):
    """处理退款工具"""
    async def _process_refund(refund_data: str) -> str:
        """处理退款，参数为JSON格式字符串"""
        try:
            # 解析JSON参数
            try:
                data = json.loads(refund_data)
            except json.JSONDecodeError:
                # 如果不是JSON，尝试当作支付ID处理
                data = {"id": refund_data.strip()}
            
            payment_id = data.get("payment_id") or data.get("id")  # 兼容两种格式
            if not payment_id:
                return "缺少必要参数：id（支付ID）"
            
            refund_reason = data.get("reason", "").strip()
            if not refund_reason:
                refund_reason = "用户申请退款"
            
            result = await payment_agent.process_refund(payment_id, refund_reason)
            
            if result["success"]:
                return f"退款处理成功：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"退款处理失败：{result['error']}"
                
        except Exception as e:
            return f"处理退款时发生错误：{str(e)}"
    
    return Tool(
        name="process_refund",
        func=_process_refund,
        description="处理退款，参数为JSON格式：{\"id\": \"支付ID\", \"reason\": \"退款原因（可选）\"}"
    )


def get_user_payments_tool(payment_agent):
    """获取用户支付记录工具"""
    async def _get_user_payments(user_id: str) -> str:
        """获取用户支付记录"""
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
        func=_get_user_payments,
        description="获取用户支付记录，参数：用户ID"
    )


def get_order_payments_tool(payment_agent):
    """获取订单支付记录工具"""
    async def _get_order_payments(order_id: str) -> str:
        """获取订单支付记录"""
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
        func=_get_order_payments,
        description="获取订单支付记录，参数：订单ID"
    )


# ----------------------------------------------------------------------
# 支付代理主类
# ----------------------------------------------------------------------
class PaymentAgent:
    """
    支付代理类 - 负责处理支付和退款相关业务
    集成真实的支付服务 API，使用模拟支付
    """

    _agent_executor: Optional[AgentExecutor] = None

    def __init__(self):
        """
        【修改】: 在 __init__ 中创建一个单一的、不带 memory 的 AgentExecutor 实例。
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
            timeout=30
        )

        tools = self._get_payment_tools()

        # 【不省略】: 提供完整的 Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是专业的支付助手，负责处理支付相关的所有业务。你的能力包括：

    1. 💳 创建支付订单（自动成功）
    2. 📊 查询支付状态（支持支付ID或订单ID）
    3. 💰 处理退款申请
    4. 📋 获取用户支付记录
    5. 📦 获取订单支付记录

    工作特点：
    - 所有支付都是模拟的，使用CNY货币
    - 支付创建后会自动变为成功状态
    - 支持通过订单ID或支付ID查询状态
    - 退款原因可以为空，会使用默认原因

    工作流程：
    1. 仔细理解用户的支付需求，并结合完整的对话历史来理解上下文。
    2. 根据需求选择合适的工具。
    3. 使用JSON格式传递参数给工具。
    4. 如果信息不足，友好地询问用户补充。
    5. 提供清晰、专业的回复。

    注意事项：
    - 支付金额最大限制：{max_amount} CNY
    - 只支持模拟支付方式
    - 创建支付时需要：订单ID（order_id）、用户ID（user_id）、金额（amount）
    - 查询支付时可以使用：支付ID（id）或 订单ID（order_id）
    - 退款时需要：支付ID（id），退款原因可选（reason）

    数据字段说明：
    - 支付ID字段名：id
    - 订单ID字段名：orderId
    - 用户ID字段名：userId
    - 创建时间字段名：createAt
    - 更新时间字段名：updateAt

    请始终保持专业、友好的服务态度。""".format(
                max_amount=self.config.MAX_PAYMENT_AMOUNT
            )),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

        # 【修改】: 创建不带 memory 的 AgentExecutor
        self._agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
        print("PaymentAgent initialized with a stateless executor.")

    def _get_payment_tools(self):
        """获取支付工具列表"""
        return [
            create_payment_tool(self),
            query_payment_status_tool(self),
            process_refund_tool(self),
            get_user_payments_tool(self),
            get_order_payments_tool(self)  # 新增：获取订单支付记录
        ]

    # async def _get_agent_executor(self, session_id: str) -> AgentExecutor:
    #     """获取或创建 AgentExecutor 实例"""
    #     message_history = RedisChatMessageHistory(
    #         session_id=f"payment_{session_id}",
    #         url=Config.REDIS_URL
    #     )
    #
    #     memory = ConversationBufferWindowMemory(
    #         chat_memory=message_history,
    #         memory_key="chat_history",
    #         return_messages=True,
    #         k=10
    #     )
    #
    #     return AgentExecutor(
    #         agent=self.agent,
    #         tools=self.tools,
    #         verbose=True,
    #         memory=memory,
    #         handle_parsing_errors=True
    #     )

    # async def process_message(self, user_input: str, session_id: str) -> str:
    # 【修改】: 重写核心方法，让 process_message 接收并使用 chat_history
    async def process_message(self, user_input: str, session_id: str, chat_history: List[BaseMessage]) -> str:
        """
        处理用户消息，使用传入的全局 chat_history 作为记忆。
        """
        self.logger.info(f"PaymentAgent 收到消息: {user_input} (Session: {session_id})")
        self.logger.info(f"--- 接收到的全局历史记录条数: {len(chat_history)} ---")

        try:
            # 在 ainvoke 中明确传入 chat_history
            response = await self._agent_executor.ainvoke({
                "input": user_input,
                "chat_history": chat_history
            })

            output = response.get("output", "PaymentAgent: 抱歉，我无法处理您的请求。")
            self.logger.info(f"PaymentAgent 响应: {output}")
            return str(output)

        except Exception as e:
            self.logger.error(f"PaymentAgent 处理消息失败: {str(e)}")
            return f"PaymentAgent: 抱歉，处理您的请求时发生错误：{str(e)}"

    # ----------------------------------------------------------------------
    # 业务逻辑方法（适配 models.py 的 AgentState）
    # ----------------------------------------------------------------------
    
    async def create_payment(self, order_id: str, user_id: str, amount: float) -> Dict[str, Any]:
        """创建支付订单（简化版，自动成功）"""
        try:
            # 验证支付金额
            if amount <= 0:
                return {"success": False, "error": "支付金额必须大于0"}

            if amount > self.config.MAX_PAYMENT_AMOUNT:
                return {"success": False, "error": f"支付金额超过限额 {self.config.MAX_PAYMENT_AMOUNT}"}

            # 创建支付订单
            payment_result = await self.payment_api.create_payment(
                order_id=order_id,
                user_id=user_id,
                amount=amount,
                status="PENDING"
            )

            if not payment_result["success"]:
                return payment_result

            payment_id = payment_result["data"].get("id")  # 使用 "id" 而不是 "payment_id"
            
            # 关键修复：立即将支付状态更新为成功
            success_result = await self.payment_api.update_payment_status(payment_id, "SUCCESS")
            
            if success_result["success"]:
                # 直接使用API返回的数据，只添加必要的业务信息
                final_payment_data = success_result["data"].copy()
                
                # 只添加API可能没有返回的关键业务信息
                final_payment_data.update({
                    "payment_time": datetime.now().isoformat(),
                    "message": "模拟支付已完成"
                })
                
                self.logger.info(f"模拟支付成功创建并完成: {payment_id} - {amount} CNY")
                
                return {
                    "success": True,
                    "data": final_payment_data
                }
            else:
                # 如果更新状态失败，返回原始创建结果，并添加警告信息
                self.logger.warning(f"支付创建成功但状态更新失败: {payment_id}")
                original_data = payment_result["data"].copy()
                original_data.update({
                    "warning": "支付已创建但状态更新失败，请稍后查询状态"
                })
                return {
                    "success": True,
                    "data": original_data
                }

        except Exception as e:
            self.logger.error(f"创建支付失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_refund(self, payment_id: str, refund_reason: str = "用户申请退款") -> Dict[str, Any]:
        """处理退款"""
        try:
            # 获取原支付信息
            payment_result = await self.payment_api.get_payment_by_id(payment_id)

            if not payment_result["success"]:
                return payment_result

            payment_data = payment_result["data"]

            # 验证支付状态
            if payment_data.get("status") not in ["SUCCESS"]:
                return {"success": False, "error": "只有成功的支付才能退款"}

            # 更新支付状态为退款中
            refund_result = await self.payment_api.update_payment_status(payment_id, "REFUNDING")

            if refund_result["success"]:
                self.logger.info(f"退款申请已提交: {payment_id}, 原因: {refund_reason}")
                
                # 模拟退款处理完成
                final_result = await self.payment_api.update_payment_status(payment_id, "REFUNDED")
                
                return {
                    "success": True,
                    "data": {
                        "id": payment_id,  # 使用 "id" 而不是 "payment_id"
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
                # 格式化支付记录
                payments = result["data"]
                if not isinstance(payments, list):
                    payments = [payments] if payments else []
                
                formatted_payments = []

                for payment in payments:
                    formatted_payment = {
                        "id": payment.get("id"),  # 使用 "id" 而不是 "payment_id"
                        "orderId": payment.get("orderId"),  # 保持与API一致
                        "userId": payment.get("userId"),    # 保持与API一致
                        "amount": payment.get("amount"),
                        "status": self.payment_status_map.get(payment.get("status"), payment.get("status")),
                        "createAt": payment.get("createAt", ""),  # 使用 "createAt"
                        "updateAt": payment.get("updateAt", "")   # 使用 "updateAt"
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

    async def delete_payment(self, payment_id: str) -> Dict[str, Any]:
        """删除支付记录"""
        try:
            result = await self.payment_api.delete_payment(payment_id)
            
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
        
    # 兼容性方法
    async def process_request(self, user_input: str) -> str:
        """处理用户请求（兼容性方法）"""
        return await self.process_message(user_input, "compatibility_session")

    def get_payment_help(self) -> str:
        """获取支付帮助信息"""
        help_text = f"""
        支付代理功能说明：

        🔧 核心功能：
        1. 💳 创建支付订单（自动成功）
        2. 📊 查询支付状态（支持支付ID或订单ID）
        3. 💰 处理退款申请
        4. 📋 获取用户支付记录
        5. 📦 获取订单支付记录

        💱 支付配置：
        - 支付方式：{self.config.DEFAULT_PAYMENT_METHOD}（模拟支付）
        - 支持币种：{self.config.DEFAULT_CURRENCY}
        - 最大支付金额：{self.config.MAX_PAYMENT_AMOUNT}

        📋 工具说明：
        - create_payment_order: 创建支付订单，需要订单ID、用户ID、金额
        - query_payment_status: 查询支付状态，支持支付ID或订单ID
        - process_refund: 处理退款申请，需要支付ID，退款原因可选
        - get_user_payments: 获取用户所有支付记录
        - get_order_payments: 获取指定订单的支付记录

        🔤 数据字段规范：
        - 支付ID：id
        - 订单ID：orderId  
        - 用户ID：userId
        - 创建时间：createAt
        - 更新时间：updateAt

        ⚠️ 注意：
        - 所有支付都是模拟的，创建后自动成功
        - 支持通过订单ID或支付ID查询状态
        - 退款原因可以为空，会使用默认原因
        - 此代理集成了大模型理解能力，能够智能解析用户自然语言输入
        - 与微服务API数据格式完全一致
        """
        return help_text


# 全局 PaymentAgent 实例
payment_agent_instance: Optional['PaymentAgent'] = None


async def get_payment_agent() -> 'PaymentAgent':
    global payment_agent_instance
    if payment_agent_instance is None:
        payment_agent_instance = PaymentAgent()
    return payment_agent_instance