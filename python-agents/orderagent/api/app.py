import sys
import os
import warnings
from typing import List, Dict, Any

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.agents import initialize_agent, AgentType, Tool
    from langchain.schema import AgentFinish
except ImportError:
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.agents import initialize_agent, AgentType, Tool
    from langchain.schema import AgentFinish

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from app_config import settings
from core.tools import get_tools


class OrderAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=settings.API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=0.1
        )
        self.tools = get_tools()
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5
        )
        system_message_str = "你是一个订单处理助手，负责解答用户的订单问题：1. 支持订单创建、修改、状态查询、取消与退款、物流信息查询等。创建订单时默认已完成支付。2. 当用户询问物流时，自动调用LogisticsQuery工具（需先确认订单ID）。3. 当用户需要创建订单时，自动调用CreateOrder工具。4. 当用户需要修改订单信息时，自动调用ModifyOrder工具。5. 当用户需要查询订单状态时，自动调用QueryOrderStatus工具。6. 当用户需要取消订单并退款时，自动调用RefundOrder工具。7. 无法回答的问题直接告知用户。8. 对话简洁友好，每次回复不超过3句话。请根据用户的问题，选择合适的工具进行处理，并严格按照以下格式回复：```json\n{\n    \"name\": \"工具名称\",\n    \"parameters\": {\n        \"input\": \"工具参数\"\n    }\n}\n```"
        system_message = SystemMessagePromptTemplate.from_template(system_message_str)
        self.prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            memory=self.memory,
            prompt=self.prompt,
            verbose=True
        )

    async def process_message(self, message: str) -> str:
        try:
            response = await self.agent.arun(input=message)
            return response
        except Exception as e:
            return f"处理消息时出错: {str(e)}"