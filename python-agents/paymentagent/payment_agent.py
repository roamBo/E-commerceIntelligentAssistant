from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough
from langchain.agents import create_tool_calling_agent, AgentExecutor
from typing import Dict, Any, Optional, List
import json
import logging
from config import PaymentConfig

class PaymentAgent:
    """
    支付代理类 - 负责处理支付和退款相关业务
    使用硅基流动API通过ChatOpenAI接口调用DeepSeek模型
    """

    def __init__(self, config: PaymentConfig = None):
        """
        初始化支付代理

        Args:
            config: 配置对象，如果不提供则使用默认配置
        """
        self.config = config or PaymentConfig()
        self.logger = logging.getLogger(__name__)

        # 初始化DeepSeek模型，通过硅基流动API调用
        self.llm = ChatOpenAI(
            api_key=self.config.SILICONFLOW_API_KEY,
            base_url=self.config.SILICONFLOW_BASE_URL,
            model=self.config.MODEL_NAME,
            temperature=self.config.MODEL_TEMPERATURE,
            max_tokens=self.config.MAX_TOKENS,
            timeout=30
        )

        # 初始化对话记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 创建工具集
        self.tools = self._create_tools()

        # 创建代理
        self.agent = self._create_agent()

        # 创建代理执行器
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            return_intermediate_steps=True
        )

    def _create_tools(self) -> List:
        """
        创建支付相关工具集

        Returns:
            List: 工具列表
        """
        # 使用 tool 装饰器创建工具
        @tool
        def process_payment(payment_data: str) -> str:
            """
            处理支付请求
            
            Args:
                payment_data: JSON格式的支付信息，包含 amount(金额), currency(币种), payment_method(支付方式), user_id(用户ID)
            
            Returns:
                str: 支付处理结果
            """
            return self._process_payment(payment_data)

        @tool
        def process_refund(refund_data: str) -> str:
            """
            处理退款请求
            
            Args:
                refund_data: JSON格式的退款信息，包含 transaction_id(交易ID), amount(退款金额), reason(退款原因)
            
            Returns:
                str: 退款处理结果
            """
            return self._process_refund(refund_data)

        @tool
        def check_payment_status(query_data: str) -> str:
            """
            查询支付状态
            
            Args:
                query_data: JSON格式的查询信息，包含 transaction_id(交易ID)
            
            Returns:
                str: 支付状态查询结果
            """
            return self._check_payment_status(query_data)

        @tool
        def validate_payment_info(payment_info: str) -> str:
            """
            验证支付信息
            
            Args:
                payment_info: JSON格式的支付信息
            
            Returns:
                str: 验证结果
            """
            return self._validate_payment_info(payment_info)

        return [process_payment, process_refund, check_payment_status, validate_payment_info]

    def _create_agent(self):
        """
        创建工具调用代理

        Returns:
            代理对象
        """
        # 使用 ChatPromptTemplate 创建现代化的提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的支付处理代理。你可以使用以下工具来处理用户的支付相关请求：

1. process_payment: 处理支付请求
2. process_refund: 处理退款请求  
3. check_payment_status: 查询支付状态
4. validate_payment_info: 验证支付信息

请根据用户的请求选择合适的工具来处理。如果需要调用工具，请确保提供正确的JSON格式参数。

支持的支付方式：{supported_payment_methods}
支持的币种：{supported_currencies}
最大支付金额：{max_payment_amount}
"""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # 使用 create_tool_calling_agent 创建工具调用代理
        return create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

    def _process_payment(self, input_str: str) -> str:
        """
        处理支付请求的工具函数

        Args:
            input_str: JSON格式的支付信息

        Returns:
            str: 支付处理结果
        """
        try:
            # 解析输入参数
            payment_data = json.loads(input_str)

            # 验证必要字段
            required_fields = ['amount', 'currency', 'payment_method', 'user_id']
            for field in required_fields:
                if field not in payment_data:
                    return f"错误：缺少必要字段 {field}"

            # 验证支付金额
            try:
                amount = float(payment_data['amount'])
                if amount <= 0:
                    return "错误：金额必须大于0"
                if amount > self.config.MAX_PAYMENT_AMOUNT:
                    return f"错误：金额超过单笔限额 {self.config.MAX_PAYMENT_AMOUNT}"
            except ValueError:
                return "错误：金额格式无效"

            # 验证币种
            if payment_data['currency'] not in self.config.SUPPORTED_CURRENCIES:
                return f"错误：不支持的币种，支持的币种：{', '.join(self.config.SUPPORTED_CURRENCIES)}"

            # 验证支付方式
            if payment_data['payment_method'] not in self.config.SUPPORTED_PAYMENT_METHODS:
                return f"错误：不支持的支付方式，支持的方式：{', '.join(self.config.SUPPORTED_PAYMENT_METHODS)}"

            # 模拟支付处理
            transaction_id = f"TXN_{payment_data['user_id']}_{hash(str(payment_data)) % 100000}"

            result = {
                "status": "success",
                "transaction_id": transaction_id,
                "amount": payment_data['amount'],
                "currency": payment_data['currency'],
                "payment_method": payment_data['payment_method'],
                "message": "支付处理成功",
                "created_time": "2024-01-15 10:30:00"
            }

            self.logger.info(f"支付处理完成: {transaction_id}")
            return json.dumps(result, ensure_ascii=False)

        except json.JSONDecodeError:
            return "错误：无效的JSON格式输入"
        except Exception as e:
            self.logger.error(f"支付处理失败: {str(e)}")
            return f"支付处理失败: {str(e)}"

    def _process_refund(self, input_str: str) -> str:
        """
        处理退款请求的工具函数

        Args:
            input_str: JSON格式的退款信息

        Returns:
            str: 退款处理结果
        """
        try:
            refund_data = json.loads(input_str)

            # 验证必要字段
            required_fields = ['transaction_id', 'amount', 'reason']
            for field in required_fields:
                if field not in refund_data:
                    return f"错误：缺少必要字段 {field}"

            # 验证退款金额
            try:
                amount = float(refund_data['amount'])
                if amount <= 0:
                    return "错误：退款金额必须大于0"
            except ValueError:
                return "错误：退款金额格式无效"

            # 模拟退款处理
            refund_id = f"REF_{refund_data['transaction_id']}_{hash(str(refund_data)) % 100000}"

            result = {
                "status": "success",
                "refund_id": refund_id,
                "original_transaction_id": refund_data['transaction_id'],
                "refund_amount": refund_data['amount'],
                "reason": refund_data['reason'],
                "message": "退款处理成功，预计3-5个工作日到账",
                "created_time": "2024-01-15 10:30:00"
            }

            self.logger.info(f"退款处理完成: {refund_id}")
            return json.dumps(result, ensure_ascii=False)

        except json.JSONDecodeError:
            return "错误：无效的JSON格式输入"
        except Exception as e:
            self.logger.error(f"退款处理失败: {str(e)}")
            return f"退款处理失败: {str(e)}"

    def _check_payment_status(self, input_str: str) -> str:
        """
        查询支付状态的工具函数

        Args:
            input_str: JSON格式的查询信息

        Returns:
            str: 支付状态查询结果
        """
        try:
            query_data = json.loads(input_str)

            if 'transaction_id' not in query_data:
                return "错误：缺少交易ID"

            transaction_id = query_data['transaction_id']

            # 模拟状态查询
            result = {
                "transaction_id": transaction_id,
                "status": "completed",  # completed, pending, failed, refunded
                "amount": "100.00",
                "currency": "CNY",
                "payment_method": "alipay",
                "created_time": "2024-01-15 10:30:00",
                "completed_time": "2024-01-15 10:30:15",
                "message": "支付已完成"
            }

            return json.dumps(result, ensure_ascii=False)

        except json.JSONDecodeError:
            return "错误：无效的JSON格式输入"
        except Exception as e:
            self.logger.error(f"状态查询失败: {str(e)}")
            return f"状态查询失败: {str(e)}"

    def _validate_payment_info(self, input_str: str) -> str:
        """
        验证支付信息的工具函数

        Args:
            input_str: JSON格式的支付信息

        Returns:
            str: 验证结果
        """
        try:
            payment_data = json.loads(input_str)
            validation_errors = []

            # 验证金额
            if 'amount' in payment_data:
                try:
                    amount = float(payment_data['amount'])
                    if amount <= 0:
                        validation_errors.append("金额必须大于0")
                    if amount > self.config.MAX_PAYMENT_AMOUNT:
                        validation_errors.append(f"金额超过单笔限额 {self.config.MAX_PAYMENT_AMOUNT}")
                except ValueError:
                    validation_errors.append("金额格式无效")

            # 验证币种
            if 'currency' in payment_data:
                if payment_data['currency'] not in self.config.SUPPORTED_CURRENCIES:
                    validation_errors.append(f"不支持的币种，支持的币种：{', '.join(self.config.SUPPORTED_CURRENCIES)}")

            # 验证支付方式
            if 'payment_method' in payment_data:
                if payment_data['payment_method'] not in self.config.SUPPORTED_PAYMENT_METHODS:
                    validation_errors.append(f"不支持的支付方式，支持的方式：{', '.join(self.config.SUPPORTED_PAYMENT_METHODS)}")

            result = {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors if validation_errors else None,
                "message": "支付信息验证通过" if len(validation_errors) == 0 else "支付信息验证失败"
            }

            return json.dumps(result, ensure_ascii=False)

        except json.JSONDecodeError:
            return "错误：无效的JSON格式输入"
        except Exception as e:
            return f"验证失败: {str(e)}"

    def process_request(self, user_input: str) -> str:
        """
        处理用户请求的主要入口

        Args:
            user_input: 用户输入的请求

        Returns:
            str: 代理的响应结果
        """
        try:
            # 构建输入参数
            input_data = {
                "input": user_input,
                "supported_payment_methods": ", ".join(self.config.SUPPORTED_PAYMENT_METHODS),
                "supported_currencies": ", ".join(self.config.SUPPORTED_CURRENCIES),
                "max_payment_amount": self.config.MAX_PAYMENT_AMOUNT
            }

            # 使用代理处理请求
            result = self.agent_executor.invoke(input_data)
            return result.get("output", "抱歉，无法处理您的请求")

        except Exception as e:
            self.logger.error(f"请求处理失败: {str(e)}")
            return f"处理请求时发生错误: {str(e)}"

    def get_payment_help(self) -> str:
        """
        获取支付帮助信息

        Returns:
            str: 帮助信息
        """
        help_text = f"""
        支付代理帮助信息：
        
        支持的功能：
        1. 处理支付 - 输入支付金额、币种、支付方式等信息
        2. 处理退款 - 提供交易ID和退款原因
        3. 查询状态 - 根据交易ID查询支付状态
        4. 验证信息 - 验证支付信息是否有效
        
        示例用法：
        - "我要支付100元，使用支付宝"
        - "我要退款，交易ID是TXN_12345，原因是商品有质量问题"
        - "查询交易TXN_12345的状态"
        - "验证这个支付信息：金额150元，币种CNY，支付方式微信"
        
        支持的支付方式：{', '.join(self.config.SUPPORTED_PAYMENT_METHODS)}
        支持的币种：{', '.join(self.config.SUPPORTED_CURRENCIES)}
        最大支付金额：{self.config.MAX_PAYMENT_AMOUNT}
        """
        return help_text

    def test_simple_chat(self, message: str) -> str:
        """
        测试简单的聊天功能

        Args:
            message: 测试消息

        Returns:
            str: 模型回复
        """
        try:
            messages = [
                SystemMessage(content="你是一个专业的支付助手。"),
                HumanMessage(content=message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            self.logger.error(f"测试聊天失败: {str(e)}")
            return f"测试聊天失败: {str(e)}"