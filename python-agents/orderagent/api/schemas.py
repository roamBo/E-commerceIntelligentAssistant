from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    """订单查询请求模型"""
    user_input: str  # 用户问题
    order_id: Optional[str] = None  # 可选的订单ID

class QueryResponse(BaseModel):
    """订单查询响应模型"""
    response: str  # 助手回复