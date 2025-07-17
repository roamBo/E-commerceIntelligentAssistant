# agents/order_agent.py
import logging
import asyncio
import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent, Tool

from reorganized.config import Config
from reorganized.models import AgentState


# ----------------------------------------------------------------------
# 订单代理配置 (无变化)
# ----------------------------------------------------------------------
class OrderConfig:
    """订单代理配置"""
    SILICONFLOW_API_KEY: str = Config.SILICONFLOW_API_KEY
    SILICONFLOW_BASE_URL: str = Config.SILICONFLOW_API_BASE
    MODEL_NAME: str = Config.LLM_MODEL_NAME
    Config.LLM_MODEL_NAME
    MODEL_TEMPERATURE: float = Config.LLM_TEMPERATURE
    MAX_TOKENS: int = 500
    ORDER_SERVICE_BASE_URL: str = os.environ.get("ORDER_SERVICE_BASE_URL", "http://10.172.66.224:8084/order")


# ----------------------------------------------------------------------
# 订单服务 API 封装 (修改)
# ----------------------------------------------------------------------
class OrderServiceAPI:
    """订单服务 API 封装"""

    def __init__(self, base_url: str = OrderConfig.ORDER_SERVICE_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 120
        self.logger = logging.getLogger(__name__)

    async def create_order(self, user_id: str, items: List[Dict[str, Any]], shipping_address: str, total_amount: float,
                           status: str = "PENDING_PAYMENT") -> Dict[str, Any]:
        """创建新订单（修改为匹配数据库格式）"""
        url = f"{self.base_url}/api/orders"
        data = {
            "userId": user_id,
            "totalAmount": total_amount,
            "shippingAddress": shipping_address,
            "items": items,
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
# 订单代理工具函数 (修改)
# ----------------------------------------------------------------------
def create_order_tool(order_agent):
    """创建订单工具"""

    def _create_order_sync(order_data: str) -> str:
        """同步包装器"""
        return asyncio.run(_create_order(order_data))

    async def _create_order(order_data: str) -> str:
        try:
            # 尝试解析JSON格式
            try:
                data = json.loads(order_data)
            except json.JSONDecodeError:
                # 如果不是JSON，尝试解析为自然语言地址格式
                return await order_agent._handle_natural_language_order(order_data)

            # 检查必需字段
            required_fields = ["user_id", "products", "address"]
            missing = [field for field in required_fields if field not in data]
            if missing:
                return f"❌❌ 缺少必要字段：{', '.join(missing)}"

            # 获取参数（安全处理）
            user_id = data.get("user_id", "")
            if isinstance(user_id, int):
                user极 = str(user_id)
            elif isinstance(user_id, str):
                user_id = user_id.strip()
            else:
                return "❌❌ 无效的用户ID格式"

            products = data.get("products", [])
            address = data.get("address", "")

            # 检查地址不能为空
            if not address:
                return "❌❌ 收货地址不能为空"

            # 统一地址格式为字符串
            if isinstance(address, dict):
                required_keys = ["name", "phone", "detail"]
                if not all(key in address for key in required_keys):
                    return "❌❌ 地址字典缺少必要字段：name, phone, detail"
                address_str = f"{address['name']}，{address['phone']}，{address['detail']}"
            else:
                address_str = str(address).strip()
                if not address_str:
                    return "❌❌ 收货地址不能为空"

            # 检查商品列表不能为空
            if len(products) == 0:
                return "❌❌ 商品列表不能为空"

            # 标准化商品格式并计算总金额
            valid_items = []
            total_amount = 0.0
            for item in products:
                # 处理字符串格式的商品
                if isinstance(item, str):
                    try:
                        parsed_item = json.loads(item)
                        if "product_id" in parsed_item:
                            item = parsed_item
                    except:
                        item = {"product_id": item, "quantity": 1}

                # 确保商品有product_id字段
                if "product_id" not in item:
                    return f"❌❌ 商品缺少product_id字段: {item}"

                # 处理整数类型的product_id
                product_id = str(item["product_id"]) if isinstance(item["product_id"], int) else item["product_id"]

                # 获取单价和数量
                unit_price = float(item.get("unit_price", 0.0))
                quantity = int(item.get("quantity", 1))
                item_amount = unit_price * quantity

                # 创建数据库格式的商品项
                valid_item = {
                    "productId": product_id,
                    "productName": item.get("product_name", f"产品{product_id}"),
                    "quantity": quantity,
                    "unitPrice": unit_price
                }

                valid_items.append(valid_item)
                total_amount += item_amount

            # 调用服务
            result = await order_agent.create_order(
                user_id,
                valid_items,
                address_str,
                total_amount
            )

            if result["success"]:
                return f"订单创建成功：{json.dumps(result['data'], ensure_ascii=False)}"
            else:
                return f"订单创建失败：{result['error']}"

        except Exception as e:
            return f"创建订单时发生错误：{str(e)}"

    # 修复：添加了缺少的func和coro参数
    return Tool(
        name="create_order",
        func=_create_order_sync,
        coro=_create_order,
        description=(
            "创建新订单。输入必须是包含以下字段的JSON字符串：\n"
            "- user_id: 用户ID\n"
            "- products: 商品列表，每个商品必须包含 product_id, quantity, unit_price\n"
            "- address: 字符串或 {name, phone, detail} 字典\n"
            "示例：{'user_id':'U123', 'products':[{'product_id':'P456','quantity':2,'unit_price':2499}], ...}"
        )
    )

def get_order_by_id_tool(order_agent):
    """根据ID获取订单工具"""

    def _get_order_by_id_sync(order_id: str) -> str:
        return asyncio.run(_get_order_by_id(order_id))

    async def _get_order_by_id(order_id: str) -> str:
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
        func=_get_order_by_id_sync,
        coro=_get_order_by_id,
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
        func=_get_orders_by_user_sync,
        coro=_get_orders_by_user,
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
                return "参数格式错误。输入必须是包含 order_id 和 status的JSON字符串。"
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
        func=_update_order_status_sync,
        coro=_update_order_status,
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
        func=_cancel_order_sync,
        coro=_cancel_order,
        description="取消一个订单，参数：订单ID"
    )


# ----------------------------------------------------------------------
# 订单代理主类 (修改)
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
        tools = [
            create_order_tool(self),
            get_order_by_id_tool(self),
            get_orders_by_user_tool(self),
            update_order_status_tool(self),
            cancel_order_tool(self)
        ]

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是专业的订单助手。你的核心任务是根据用户的指令和对话极史，调用工具来处理订单。

        **工作流程:**
        1.  **分析意图**: 仔细分析用户的最新输入和完整的对话历史，理解用户的具体需求。
        2.  **收集信息**:
            -   **创建订单时**: 必须从对话历史中提取完整信息：
                • 商品列表（product_id和数量）
                • 收货人姓名
                • 收货人联系电话
                • 详细收货地址（省市区+街道门牌号）
            -   如果缺少任何信息，必须明确要求用户提供
        3.  **调用工具**: 使用提取的信息调用创建订单工具
        4.  **订单金额**：从对话历史中提取
        5.  **响应用户**: 根据工具结果生成回复

        **重要规则:**
        - 收货地址必须是完整的省市区+街道门牌号
        -当调用工具函数时打印出使用了哪个工具函数
        -从对话历史中计算订单金额并正确记录
        -当用户要求查询自己的所有订单信息时，优先调用工具函数查询，而不是从chathistory中解析。
        - 如果用户未提供收货信息，返回固定格式提示：
          "请提供收货信息：[姓名]，[电话]，[完整地址]"
        - 绝不虚构信息"""),
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
    # 业务逻辑方法 (修改)
    # ----------------------------------------------------------------------
    async def create_order(
            self,
            user_id: str,
            items: List[Dict[str, Any]],  # 商品列表
            shipping_address: str,  # 地址
            total_amount: float  # 总金额
    ) -> Dict[str, Any]:
        """创建新订单（修正参数顺序）"""
        try:
            # 调用API（匹配数据库格式）
            return await self.order_api.create_order(
                user_id,
                items,
                shipping_address,
                total_amount
            )
        except Exception as e:
            self.logger.error(f"创建订单失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_order_by_id(self, order_id: str) -> Dict[str, Any]:
        """根据订单ID获取订单信息"""
        return await self.order_api.get_order_by_id(order_id)

    async def get_orders_by_user(self, user_id: str) -> Dict[str, Any]:
        """获取用户的所有订单"""
        return await self.order_api.get_orders_by_user(user_id)

    async def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """更新订单状态"""
        return await self.order_api.update_order_status(order_id, status)

    async def _handle_natural_language_order(self, input_text: str) -> str:
        """处理自然语言格式的订单信息"""
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "将用户输入解析为结构化订单数据。注意："
             "1. 商品字段可能是数组或单个商品对象\n"
             "2. 单个商品格式: {'product_id':'..','quantity':1}\n"
             "3. 自动为缺失quantity字段补默认值1\n"
             "4. 必须提取总金额(total_amount)\n"  # 新增金额提取要求
             "5. 输出必须是JSON格式，包含user_id, products, address, total_amount字段")  # 增加金额字段
        ])

        llm = ChatOpenAI(
            model=self.config.MODEL_NAME,
            temperature=0,
            api_key=self.config.SILICONFLOW_API_KEY,
            base_url=self.config.SILICONFLOW_BASE_URL
        )
        parser = JsonOutputParser()

        try:
            # 解析自然语言输入
            chain = prompt | llm | parser
            structured_data = await chain.ainvoke({"input": input_text})
            self.logger.info(f"自然语言解析结果：{structured_data}")
            if not structured_data.get("products"):
                return "❌ 解析失败：未识别到商品信息"

            if not structured_data.get("address"):
                return "❌ 解析失败：未识别到收货地址"
                # +++ 新增：直接使用结构化数据中的单价 +++
                valid_items = []
                total_amount = 0.0
                for item in structured_data["products"]:  # 直接使用已解析数据
                    unit_price = float(item["unit_price"])  # 确保单价存在
                    quantity = int(item.get("quantity", 1))

                    valid_item = {
                        "productId": str(item["product_id"]),
                        "productName": item.get("product_name", f"产品{item['product_id']}"),
                        "quantity": quantity,
                        "unitPrice": unit_price  # 确保传递单价
                    }
                    valid_items.append(valid_item)
                    total_amount += unit_price * quantity  # 计算总金额

                # 调用服务时传递计算的总金额
                result = await self.create_order(
                    structured_data["user_id"],
                    valid_items,
                    address_str,
                    total_amount  # 关键修复点
                )

            # 递归调用创建订单方法
            return await self._create_order_from_nlp(structured_data)

        except Exception as e:
            return f"❌ 订单解析失败：{str(e)}"

    async def _create_order_from_nlp(self, structured_data: dict) -> str:
        """处理从自然语言解析出的结构化数据（添加金额提取与验证）"""
        try:
            # 确保所有必要字段都存在
            required_fields = ["user_id", "products", "address"]
            missing = [field for field in required_fields if field not in structured_data]
            if missing:
                return f"❌❌ 缺少必要字段：{', '.join(missing)}"

            # 获取地址信息
            address = structured_data["address"]
            if not address:
                return "❌❌ 收货地址不能为空"

            # 统一地址格式为字符串
            if isinstance(address, dict):
                # 确保字典包含必要字段
                required_keys = ["name", "phone", "detail"]
                if not all(key in address for key in required_keys):
                    return "❌❌ 地址字典缺少必要字段：name, phone, detail"
                address_str = f"{address['name']}，{address['phone']}，{address['detail']}"
            else:
                address_str = str(address).strip()
                if not address_str:
                    return "❌❌ 收货地址不能为空"

            # 处理商品列表
            products = structured_data["products"]
            if not products:
                return "❌❌ 商品列表不能为空"

            # 场景1：用户输入的是单一商品字典
            if isinstance(products, dict):
                products = [products]  # 包装成列表

            # 场景2：用户输入的是字符串格式商品ID
            elif isinstance(products, str):
                try:
                    # 尝试解析为JSON
                    products = json.loads(products)
                except:
                    # 非JSON字符串：视为单一商品ID
                    products = [{"product_id": products, "quantity": 1}]

            # 验证商品列表类型
            if not isinstance(products, list):
                return "❌❌ 商品列表必须是数组格式"

            # ========== 金额提取与验证 ==========
            # 1. 尝试从结构化数据中提取总金额
            total_amount = 0.0
            if 'total_amount' in structured_data:
                try:
                    total_amount = float(structured_data['total_amount'])
                    self.logger.info(f"从解析数据提取总金额: ¥{total_amount:.2f}")
                except (TypeError, ValueError):
                    self.logger.warning("无法转换total_amount为数字，将使用0.0")
                    total_amount = 0.0

            # 2. 计算商品实际总金额
            calculated_amount = 0.0
            valid_items = []
            for item in products:
                # 确保商品有product_id字段
                if "product_id" not in item:
                    return f"❌❌ 商品缺少product_id字段: {item}"

                # 处理整数类型的product_id
                product_id = str(item["product_id"]) if isinstance(item["product_id"], int) else item["product_id"]

                # 获取单价和数量
                unit_price = float(item.get("unit_price", 0.0))
                quantity = int(item.get("quantity", 1))

                # 创建数据库格式的商品项
                valid_item = {
                    "productId": product_id,
                    "productName": item.get("product_name", f"产品{product_id}"),
                    "quantity": quantity,
                    "unitPrice": unit_price
                }
                valid_items.append(valid_item)

                # 累加计算金额
                item_total = unit_price * quantity
                calculated_amount += item_total
                self.logger.info(f"商品计算: {product_id} × {quantity} @ ¥{unit_price:.2f} = ¥{item_total:.2f}")

            self.logger.info(f"商品总金额计算: ¥{calculated_amount:.2f}")

            # 3. 金额验证与决策
            if total_amount > 0:
                # 存在解析金额时进行验证
                if abs(total_amount - calculated_amount) > 0.01:  # 考虑浮点精度
                    amount_difference = abs(total_amount - calculated_amount)
                    percentage_diff = abs(total_amount - calculated_amount) / total_amount

                    if percentage_diff > 0.1:  # 差异超过10%
                        error_msg = (f"❌❌ 金额不一致：解析金额¥{total_amount:.2f} "
                                     f"与商品总价¥{calculated_amount:.2f}不符，差异{percentage_diff:.2%}")
                        self.logger.error(error_msg)
                        return error_msg
                    else:
                        self.logger.warning(f"金额差异在可接受范围（{amount_difference:.2f}），使用解析金额")
                        final_amount = total_amount
                else:
                    self.logger.info("金额一致，使用解析金额")
                    final_amount = total_amount
            else:
                self.logger.info("未解析到金额，使用计算金额")
                final_amount = calculated_amount

            # 最终金额验证
            if final_amount <= 0:
                return "❌❌ 订单金额必须大于0"

            self.logger.info(f"最终使用金额: ¥{final_amount:.2f}")
            # ========== 结束金额处理 ==========

            # 调用创建订单服务
            result = await self.create_order(
                structured_data["user_id"],
                valid_items,  # 商品列表
                address_str,  # 地址
                final_amount  # 总金额 - 确保传递
            )

            if result["success"]:
                # 在响应中包含金额信息
                order_data = result['data']
                order_data['totalAmount'] = final_amount  # 确保响应包含正确金额
                return f"订单创建成功：{json.dumps(order_data, ensure_ascii=False)}"
            else:
                return f"订单创建失败：{result['error']}"
        except Exception as e:
            return f"创建订单时发生错误：{str(e)}"


# ----------------------------------------------------------------------
# 全局 OrderAgent 实例管理 (无变化)
# ----------------------------------------------------------------------
order_agent_instance: Optional['OrderAgent'] = None


async def get_order_agent() -> 'OrderAgent':
    global order_agent_instance
    if order_agent_instance is None:
        order_agent_instance = OrderAgent()
    return order_agent_instance