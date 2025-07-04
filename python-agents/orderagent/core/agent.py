import sys
import os
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, initialize_agent, Tool
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
import redis

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from app_config import settings
from core.tools import get_tools

redis_client = redis.Redis(host='localhost', port=6379, db=0)


class OrderAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.API_KEY,
            base_url=settings.API_URL,
            model_name=settings.MODEL_NAME,
            temperature=0.3
        )
        self.tools = get_tools()
        self.message_history = ChatMessageHistory()
        self._load_chat_history()
        system_message_str = "你是一个订单处理助手，负责解答用户的订单问题：1. 支持查询订单状态、物流信息、预计送达时间等。创建订单时默认已完成支付。2. 当用户询问物流时，自动调用LogisticsQuery工具（需先确认订单ID)。3. 支持创建、修改、取消、退款订单，查询订单状态。4. 无法回答的问题直接告知用户。5. 对话简洁友好，每次回复不超过3句话。"
        system_message = SystemMessage(content=system_message_str)
        self.prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        self.agent = self._initialize_agent()

    def _initialize_agent(self) -> AgentExecutor:
        llm_with_tools = self.llm.bind(functions=self._tools_to_functions())

        agent = (
                {
                    "input": lambda x: x["input"],
                    "chat_history": lambda x: self.message_history.messages[-5:] if len(
                        self.message_history.messages) > 0 else [],
                    "agent_scratchpad": lambda x: format_to_openai_functions(x["intermediate_steps"])
                }
                | self.prompt
                | llm_with_tools
                | OpenAIFunctionsAgentOutputParser()
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True
        )

    def _tools_to_functions(self) -> list:
        return [{
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "工具输入参数"}
                },
                "required": ["input"]
            }
        } for tool in self.tools]

    def run(self, user_input: str) -> str:
        try:
            self.message_history.add_user_message(user_input)
            response = self.agent.invoke({"input": user_input})
            if "output" in response:
                self.message_history.add_ai_message(response["output"])
                self._save_chat_history()
                return response["output"]
            return "未能生成有效响应"
        except Exception as e:
            error_msg = f"处理请求时出错: {str(e)}"
            self.message_history.add_ai_message(error_msg)
            self._save_chat_history()
            return error_msg

    def _save_chat_history(self):
        try:
            history = []
            for message in self.message_history.messages:
                if isinstance(message, HumanMessage):
                    history.append({"type": "human", "data": {"content": message.content}})
                elif isinstance(message, AIMessage):
                    history.append({"type": "ai", "data": {"content": message.content}})
            redis_client.set('chat_history', json.dumps(history))
        except Exception as e:
            print(f"保存对话历史失败: {str(e)}")

    def _load_chat_history(self):
        try:
            history_data = redis_client.get('chat_history')
            if history_data:
                history = json.loads(history_data)
                for item in history:
                    if item["type"] == "human":
                        self.message_history.add_user_message(item["data"]["content"])
                    elif item["type"] == "ai":
                        self.message_history.add_ai_message(item["data"]["content"])
        except Exception as e:
            print(f"加载对话历史失败: {str(e)}")

    def clear_chat_history(self):
        try:
            redis_client.delete('chat_history')
            self.message_history.messages = []
            print("聊天记录已清空。")
        except Exception as e:
            print(f"清空聊天记录失败: {str(e)}")