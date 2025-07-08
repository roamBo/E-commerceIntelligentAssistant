import time
import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 后续代码保持不变
import uvicorn
from typing import TypedDict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.graph import StateGraph, END

# 导入 Agent 类
from orderagent.core.agent import OrderAgent
# 正确导入方式（从顶层包开始）
from guideagent.agent import GuideAgent
from paymentagent.payment_agent import PaymentAgent

# 定义状态类型 (TypedDict)
class AgentState(TypedDict):
    order_id: Optional[str]
    payment_status: Optional[str]
    order_status: Optional[str]
    guide_info: Optional[dict]
    error: Optional[str]
    request_data: dict  # 存储原始请求数据

# 初始化 Agent 实例
order_agent = OrderAgent()
guide_agent = GuideAgent()
payment_agent = PaymentAgent()

# 创建 StateGraph 实例
workflow = StateGraph(AgentState)

# 定义节点函数
def process_order(state: AgentState) -> AgentState:
    """订单处理节点"""
    print("Order Agent processing...")
    try:
        result = order_agent.create_order(
            user_id=state["request_data"]["user_id"],
            product_id=state["request_data"]["product_id"],
            quantity=state["request_data"]["quantity"],
            price=state["request_data"]["price"]
        )
        return {**state, "order_id": result["order_id"], "order_status": "created"}
    except Exception as e:
        return {**state, "error": f"Order processing failed: {str(e)}"}

def process_payment(state: AgentState) -> AgentState:
    """支付处理节点"""
    print("Payment Agent processing...")
    if not state.get("order_id"):
        return {**state, "error": "No order ID provided for payment"}

    try:
        result = payment_agent.process_payment(
            order_id=state["order_id"],
            amount=state["request_data"]["price"]
        )
        return {**state, "payment_status": "completed", "order_status": "paid"}
    except Exception as e:
        return {**state, "error": f"Payment processing failed: {str(e)}"}

def process_guide(state: AgentState) -> AgentState:
    """指南生成节点"""
    print("Guide Agent processing...")
    if not state.get("order_id"):
        return {**state, "error": "No order ID provided for guide"}

    try:
        result = guide_agent.generate_guide(
            order_id=state["order_id"],
            product_id=state["request_data"]["product_id"]
        )
        return {**state, "guide_info": result}
    except Exception as e:
        return {**state, "error": f"Guide generation failed: {str(e)}"}

# 添加节点到 StateGraph
workflow.add_node("order", process_order)
workflow.add_node("payment", process_payment)
workflow.add_node("guide", process_guide)

# 设置图结构
workflow.set_entry_point("order")  # 设置入口节点
workflow.add_edge("order", "payment")  # order → payment
workflow.add_edge("payment", "guide")  # payment → guide
workflow.add_edge("guide", END)  # guide → 结束

# 编译图 (必须步骤)
chain = workflow.compile()

# FastAPI 应用
app = FastAPI(title="Agent Orchestrator Service")

@app.post("/create_order")
async def create_order(request: dict):
    """订单创建接口"""
    initial_state = AgentState(
        request_data=request,
        order_id=None,
        payment_status=None,
        order_status=None,
        guide_info=None,
        error=None
    )

    try:
        result = chain.invoke(initial_state)
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 主函数
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)