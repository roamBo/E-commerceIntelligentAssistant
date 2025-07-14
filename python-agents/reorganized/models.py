# models.py
from typing import List, Optional, Dict, Any, TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

# --- Agent 内部数据结构 ---
class Recommendation(BaseModel):
    product_name: str = Field(..., description="推荐的商品名称")
    reasons: List[str] = Field(..., description="2-3条推荐理由，需突出商品与用户需求的匹配点，并包含关键信息")

class FinalResponse(BaseModel):
    """这是用于格式化最终响应的数据结构。"""
    demand_analysis: str = Field(..., description="用1句话精准概括的用户需求")
    search_keyword: str = Field(..., description="根据用户需求确定的、用于调用search_products工具的搜索关键词")
    recommendations: List[Recommendation] = Field(..., description="基于搜索结果生成的商品推荐列表")

# --- 外部商品 API 返回的数据结构 (示例) ---
# 如果使用外部API，这个模型用于解析API返回的单个商品数据
class Product(BaseModel):
    _id: str
    sku: str
    name: str
    description: str
    category: str
    brand: str
    price: float
    stock: int
    status: str
    tags: List[str]
    imageUrl: Optional[str] = None
    createTime: Optional[str] = None
    updateTime: Optional[str] = None
    rating: Optional[float] = None
    reviewCount: Optional[int] = None
    specifications: Optional[str] = None

# --- API 请求体模型 ---
class ChatRequest(BaseModel):
    user_input: str = Field(..., description="用户的输入消息")
    session_id: str = Field(..., description="用户的会话ID，用于区分不同用户的对话历史")
    user_id: str = Field(..., description="用户唯一标识符")

# --- API 响应体模型 ---
class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent 返回的推荐报告或消息")
    session_id: str = Field(..., description="当前会话的ID")

# --- LangGraph 状态定义 ---
class AgentState(TypedDict):
    """
    LangGraph 中用于在不同 Agent 之间传递的状态。
    """
    user_input: str # 用户当前输入
    session_id: str # 会话ID
    user_id: str
    chat_history: List[BaseMessage] # 整个对话历史，由监管者Agent维护
    # 各个子Agent的输出或中间结果
    guide_agent_output: Optional[str]
    order_agent_output: Optional[str]
    payment_agent_output: Optional[str]
    # 监管者Agent的决策结果
    next_agent: Optional[str] # 决定下一个要调用的子Agent
