# api/app.py（使用 LangFlow 替代 LangGraph）
import sys
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool

# 获取项目根目录并添加到sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from app_config import settings
from core.tools import get_tools


class OrderAgent:
    def __init__(self):
        # 加载模型
        self.llm = ChatOpenAI(
            api_key=settings.API_KEY,
            base_url=settings.API_URL,
            model_name=settings.MODEL_NAME,
            temperature=0.3
        )

        # 加载工具
        self.tools = get_tools()

        # 配置内存
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5  # 保留最近5轮对话
        )

        # 配置提示模板
        system_message = SystemMessagePromptTemplate.from_template("""
        你是一个订单处理助手，负责解答用户的订单问题：
        1. 支持订单创建、修改、状态查询、取消与退款、物流信息查询等。
        2. 当用户询问物流时，自动调用LogisticsQuery工具（需先确认订单ID）。
        3. 当用户需要创建订单时，自动调用CreateOrder工具。
        4. 当用户需要修改订单信息时，自动调用ModifyOrder工具。
        5. 当用户需要查询订单状态时，自动调用QueryOrderStatus工具。
        6. 当用户需要取消订单并退款时，自动调用RefundOrder工具。
        7. 无法回答的问题直接告知用户。
        8. 对话简洁友好，每次回复不超过3句话。
        """)

        self.prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        # 初始化代理
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            agent_kwargs={"prompt": self.prompt}
        )

    def run(self, user_input: str) -> str:
        """处理用户输入并返回响应"""
        return self.agent.run(input=user_input)


if __name__ == "__main__":
    # 测试代码示例
    agent = OrderAgent()
    print(agent.run("你好，请帮我创建一个新订单"))