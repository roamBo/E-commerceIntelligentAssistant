import sys
import os
import warnings
from typing import List, Dict, Any

# 忽略 LangChain 弃用警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

try:
    # 尝试导入新版本模块
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.agents import initialize_agent, AgentType, Tool
    from langchain.schema import AgentFinish
except ImportError:
    # 回退到旧版本导入方式
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.agents import initialize_agent, AgentType, Tool
    from langchain.schema import AgentFinish

# 获取项目根目录并添加到sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from app_config import settings
from core.tools import get_tools


class OrderAgent:
    def __init__(self):
        # 初始化语言模型
        self.llm = ChatOpenAI(
            openai_api_key=settings.API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=0.1
        )

        # 初始化工具
        self.tools = get_tools()

        # 初始化内存
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5
        )

        # 定义系统提示（确保三引号字符串正确闭合）
        system_message = """
        你是一个订单处理助手，负责解答用户的订单问题：
        1. 支持订单创建、修改、状态查询、取消与退款、物流信息查询等。
        2. 当用户询问物流时，自动调用LogisticsQuery工具（需先确认订单ID）。
        3. 当用户需要创建订单时，自动调用CreateOrder工具。
        4. 当用户需要修改订单信息时，自动调用ModifyOrder工具。
        5. 当用户需要查询订单状态时，自动调用QueryOrderStatus工具。
        6. 当用户需要取消订单并退款时，自动调用RefundOrder工具。
        7. 无法回答的问题直接告知用户。
        8. 对话简洁友好，每次回复不超过3句话。

        请根据用户的问题，选择合适的工具进行处理，并严格按照以下格式回复：
        ```json
        {
            "name": "工具名称",
            "parameters": {
                "input": "工具参数"
            }
        }
        ```
        """

        # 创建提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # 初始化代理
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            memory=self.memory,
            prompt=self.prompt,
            verbose=True
        )

    async def process_message(self, message: str) -> str:
        """处理用户消息并返回响应"""
        try:
            response = await self.agent.arun(input=message)
            return response
        except Exception as e:
            return f"处理消息时出错: {str(e)}"