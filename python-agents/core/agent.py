# core/agent.py
import sys
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.tools import Tool

# 解决导入路径问题
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
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input",
            output_key="output"
        )

        # 配置提示模板
        system_message = SystemMessagePromptTemplate.from_template("""
        你是一个订单处理助手，负责解答用户的订单问题：
        1. 支持查询订单状态、物流信息、预计送达时间等。
        2. 当用户询问物流时，自动调用LogisticsQuery工具（需先确认订单ID）。
        3. 支持创建、修改、取消、退款订单，查询订单状态。
        4. 无法回答的问题直接告知用户。
        5. 对话简洁友好，每次回复不超过3句话。
        """)

        self.prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        # 使用新的链式API初始化Agent
        self.agent = RunnablePassthrough.assign(
            chat_history=lambda x: self.memory.load_memory_variables(x)["chat_history"]
        ) | self.prompt | self.llm | self._create_tool_router()

    def _create_tool_router(self) -> RunnableLambda:
        """创建工具路由器，处理LLM输出并调用适当的工具"""
        tool_dict = {tool.name: tool for tool in self.tools}

        def route_to_tool(llm_output):
            # 检查是否为工具调用格式
            if isinstance(llm_output, dict) and "name" in llm_output and "parameters" in llm_output:
                tool_name = llm_output["name"]
                tool_input = llm_output["parameters"].get("input", "")

                if tool_name in tool_dict:
                    return tool_dict[tool_name].run(tool_input)
                else:
                    return f"工具 {tool_name} 不存在，请直接回答用户问题。"
            else:
                return llm_output  # 不是工具调用，直接返回LLM输出

        return RunnableLambda(route_to_tool)

    def run(self, user_input: str) -> str:
        """处理用户输入并返回响应"""
        # 保存用户输入到内存
        self.memory.save_context({"input": user_input}, {"output": ""})

        # 执行Agent
        response = self.agent.invoke({"input": user_input})

        # 保存LLM响应到内存
        self.memory.save_context({"input": user_input}, {"output": response})

        return response