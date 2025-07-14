import os
import sys
from typing import Dict, Any, Optional, List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import BaseMessage

# 修正导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from config import Config
from tools import search_products, format_final_response

# --- 配置LLM ---
llm = ChatOpenAI(
    model=Config.LLM_MODEL_NAME,
    temperature=Config.LLM_TEMPERATURE,
    api_key=Config.SILICONFLOW_API_KEY,
    base_url=Config.SILICONFLOW_API_BASE
)

# --- 创建Prompt模板 ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """你是专业的商品推荐专家。你的任务流程如下：
1.  仔细分析用户的需求和完整的对话历史，以理解上下文。
2.  你绝不能使用自身的知识来提供商品信息。所有商品信息都必须通过调用 `search_products` 工具来获取。
3.  `search_products` 工具现在支持多种查询参数，包括名称、分类、品牌、价格范围、标签和库存状态。请根据用户需求，尽可能精确地使用这些参数。
4.  如果 `search_products` 工具返回空结果，你必须明确告知用户“没有找到相关商品”。
5.  在获得所有必要信息（需求分析、搜索关键词、商品详情）后，必须调用 `format_final_response` 工具来生成最终的、结构化的推荐报告。这是最后一步。
6.  在生成的报告中，商品名称之后你应同步提供商品对应的id，并用product_id标明"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# --- Agent 可用工具 ---
agent_tools = [search_products, format_final_response]


class GuideAgent:
    # 创建一个类级别、无状态的 AgentExecutor
    _agent_executor: Optional[AgentExecutor] = None

    def __init__(self):
        """
        初始化一个无状态的 AgentExecutor。
        记忆将在每次调用时通过 chat_history 参数动态传入。
        """
        base_agent = create_tool_calling_agent(
            llm=llm,
            tools=agent_tools,
            prompt=prompt_template
        )
        # 初始化一个不带 memory 的 AgentExecutor
        self._agent_executor = AgentExecutor(
            agent=base_agent,
            tools=agent_tools,
            verbose=True,
            handle_parsing_errors=True,  # 增加错误处理
        )
        print("GuideAgent initialized with a stateless executor.")

    async def process_message(self, user_input: str, session_id: str, user_id: str,chat_history: List[BaseMessage]) -> str:
        """
        处理用户消息，直接使用由监管者传入的全局 chat_history 作为记忆。
        """
        print(f"--- GuideAgent 正在处理请求 (Session: {session_id}) ---")
        print(f"--- 接收到的全局历史记录 (最近3条): {chat_history[-3:]}")

        try:
            # 在 ainvoke 中明确传入 chat_history，实现全局上下文注入
            response = await self._agent_executor.ainvoke({
                "input": user_input,
                "chat_history": chat_history
            })

            final_report = response.get('output', "未能生成有效响应")
            return str(final_report)
        except Exception as e:
            error_msg = f"GuideAgent 在处理请求时出错: {str(e)}"
            print(f"ERROR: {error_msg}")
            return error_msg


# 全局 GuideAgent 实例
guide_agent_instance: Optional['GuideAgent'] = None


async def get_guide_agent() -> 'GuideAgent':
    """获取全局 GuideAgent 实例"""
    global guide_agent_instance
    if guide_agent_instance is None:
        guide_agent_instance = GuideAgent()
    return guide_agent_instance
