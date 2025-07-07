# agent.py
import os
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

from config import Config
from tools import search_products, format_final_response # 导入工具

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
1.  仔细分析用户的需求。
2.  你绝不能使用自身的知识来提供商品信息。所有商品信息都必须通过调用 `search_products` 工具来获取。
3.  `search_products` 工具现在支持多种查询参数，包括名称、分类、品牌、价格范围、标签和库存状态。请根据用户需求，尽可能精确地使用这些参数。
4.  如果 `search_products` 工具返回空结果，你必须明确告知用户“没有找到相关商品”。
5.  在获得所有必要信息（需求分析、搜索关键词、商品详情）后，必须调用 `format_final_response` 工具来生成最终的、结构化的推荐报告。这是最后一步。"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# --- Agent 可用工具 ---
agent_tools = [search_products, format_final_response]

# --- 构建 Agent ---
base_agent = create_tool_calling_agent(
    llm=llm,
    tools=agent_tools,
    prompt=prompt_template
)

# --- AgentExecutor 缓存 ---
agent_executors_cache: Dict[str, AgentExecutor] = {}

def get_agent_executor(session_id: str) -> AgentExecutor:
    """
    根据 session_id 获取或创建 AgentExecutor 实例。
    """
    if session_id not in agent_executors_cache:
        print(f"--- 为新会话创建 AgentExecutor: {session_id} ---")
        message_history = RedisChatMessageHistory(
            session_id=session_id,
            url=Config.REDIS_URL
        )
        memory = ConversationBufferWindowMemory(
            chat_memory=message_history,
            memory_key="chat_history",
            return_messages=True,
            k=5
        )
        executor = AgentExecutor(
            agent=base_agent,
            tools=agent_tools,
            verbose=True, # 生产环境通常设置为False
            memory=memory
        )
        agent_executors_cache[session_id] = executor
    else:
        print(f"--- 使用现有 AgentExecutor: {session_id} ---")
    return agent_executors_cache[session_id]
