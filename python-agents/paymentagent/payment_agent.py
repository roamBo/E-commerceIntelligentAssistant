from langchain.llms import OpenAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from typing import Dict, Any, Optional
import json
import logging

class PaymentAgent:
    """
    支付代理类 - 负责处理支付和退款相关业务
    使用硅基流动API通过OpenAI接口调用DeepSeek模型
    """

    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1"):
        """
        初始化支付代理

        Args:
            api_key: 硅基流动的API密钥
            base_url: API基础URL，默认为硅基流动地址
        """
        self.logger = logging.getLogger(__name__)

        # 初始化DeepSeek模型，通过硅基流动API调用
        self.llm = OpenAI(
            openai_api_key=api_key,
            openai_api_base=base_url,
            model_name="Pro/deepseek-ai/DeepSeek-R1",  # 根据硅基流动支持的模型名称调整
            temperature=0.1,  # 降低温度以提高准确性
            # max_tokens=2000
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
            max_iterations=5
        )

    def _create_tools(self) -> list:
        """
        创建支付相关工具集

        Returns:
            list: 工具列表
        """
        tools = [
            Tool(
                name="process_payment",
                description="处理支付请求。输入格式: {'amount': 金额, 'currency': 币种, 'payment_method': 支付方式, 'user_id': 用户ID}",
                func=self._process_payment
            ),
            Tool(
                name="process_refund",
                description="处理退款请求。输入格式: {'transaction_id': 交易ID, 'amount': 退款金额, 'reason': 退款原因}",
                func=self._process_refund
            ),
            Tool(
                name="check_payment_status",
                description="查询支付状态。输入格式: {'transaction_id': 交易ID}",
                func=self._check_payment_status
            ),
            Tool(
                name="validate_payment_info",
                description="验证支付信息。输入格式: {'payment_data': 支付数据字典}",
                func=self._validate_payment_info
            )
        ]
        return tools

    def _create_agent(self):
        """
        创建React代理

        Returns:
            代理对象
        """
        # 定义代理提示模板
        prompt_template = """
        你是一个专业的支付处理代理，负责处理支付和退款相关事务。
        
        你的职责包括：
        1. 处理用户的支付请求
        2. 处理退款申请
        3. 查询交易状态
        4. 验证支付信息的有效性
        5. 提供支付相关的帮助和建议
        
        请始终保持专业、准确、安全的态度处理每一个请求。
        对于敏感的支付信息，要格外小心处理。
        
        可用工具：
        {tools}
        
        工具名称：{tool_names}
        
        请按照以下格式进行思考和行动：
        
        Question: 用户的输入问题
        Thought: 我需要思考如何处理这个请求
        Action: 选择要使用的工具
        Action Input: 工具的输入参数
        Observation: 工具执行的结果
        ... (这个思考/行动/观察的过程可以重复多次)
        Thought: 我现在知道最终答案了
        Final Answer: 给用户的最终回复
        
        开始！
        
        Question: {input}
        Thought: {agent_scratchpad}
        """

        prompt = PromptTemplate.from_template(prompt_template)

        return create_react_agent(
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

            # 这里是支付处理的模拟逻辑
            # 实际项目中需要调用真实的支付接口
            required_fields = ['amount', 'currency', 'payment_method', 'user_id']

            # 验证必要字段
            for field in required_fields:
                if field not in payment_data:
                    return f"错误：缺少必要字段 {field}"

            # 模拟支付处理
            transaction_id = f"TXN_{payment_data['user_id']}_{hash(str(payment_data)) % 100000}"

            result = {
                "status": "success",
                "transaction_id": transaction_id,
                "amount": payment_data['amount'],
                "currency": payment_data['currency'],
                "message": "支付处理成功"
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

            # 模拟退款处理
            refund_id = f"REF_{refund_data['transaction_id']}_{hash(str(refund_data)) % 100000}"

            result = {
                "status": "success",
                "refund_id": refund_id,
                "original_transaction_id": refund_data['transaction_id'],
                "refund_amount": refund_data['amount'],
                "reason": refund_data['reason'],
                "message": "退款处理成功，预计3-5个工作日到账"
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

            # 模拟状态查询
            # 实际项目中需要查询数据库或调用支付服务商API
            transaction_id = query_data['transaction_id']

            result = {
                "transaction_id": transaction_id,
                "status": "completed",  # completed, pending, failed, refunded
                "amount": "100.00",
                "currency": "CNY",
                "created_time": "2024-01-15 10:30:00",
                "completed_time": "2024-01-15 10:30:15"
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
                    if amount > 10000:  # 假设单笔限额10000
                        validation_errors.append("金额超过单笔限额")
                except ValueError:
                    validation_errors.append("金额格式无效")

            # 验证币种
            supported_currencies = ['CNY', 'USD', 'EUR']
            if 'currency' in payment_data:
                if payment_data['currency'] not in supported_currencies:
                    validation_errors.append(f"不支持的币种，支持的币种：{', '.join(supported_currencies)}")

            # 验证支付方式
            supported_methods = ['alipay', 'wechat', 'bank_card', 'paypal']
            if 'payment_method' in payment_data:
                if payment_data['payment_method'] not in supported_methods:
                    validation_errors.append(f"不支持的支付方式，支持的方式：{', '.join(supported_methods)}")

            if validation_errors:
                result = {
                    "valid": False,
                    "errors": validation_errors
                }
            else:
                result = {
                    "valid": True,
                    "message": "支付信息验证通过"
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
            result = self.agent_executor.invoke({"input": user_input})
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
        help_text = """
        支付代理帮助信息：
        
        支持的功能：
        1. 处理支付 - 输入支付金额、币种、支付方式等信息
        2. 处理退款 - 提供交易ID和退款原因
        3. 查询状态 - 根据交易ID查询支付状态
        4. 验证信息 - 验证支付信息是否有效
        
        示例用法：
        - "我要支付100元，使用支付宝"
        - "我要退款，交易ID是TXN_12345"
        - "查询交易TXN_12345的状态"
        
        支持的支付方式：支付宝、微信、银行卡、PayPal
        支持的币种：人民币(CNY)、美元(USD)、欧元(EUR)
        """
        return help_text