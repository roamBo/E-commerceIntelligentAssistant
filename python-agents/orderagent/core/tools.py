# core/tools.py
from langchain.tools import Tool
from typing import Optional


def create_order(input: str) -> str:
    """创建新订单，参数格式：商品名称,数量,收货地址,支付方式"""
    try:
        product_name, quantity, address, payment_method = input.split(',', 3)
        quantity = int(quantity.strip())
    except ValueError:
        return "参数格式错误，请使用：商品名称,数量,收货地址,支付方式"

    order_id = f"ORD-{hash(product_name + address) % 1000000:06d}"
    return (f"已成功创建订单 {order_id} 并完成支付：\n"
            f"- 商品: {product_name.strip()} x {quantity}\n"
            f"- 收货地址: {address.strip()}\n"
            f"- 支付方式: {payment_method.strip()}\n\n"
            "你可以使用订单ID查询订单状态或物流信息。")


def modify_order(input: str) -> str:
    """修改订单信息，参数格式：订单ID,修改内容（如：收货地址=北京市朝阳区）"""
    try:
        order_id, modification = input.split(',', 1)
        return f"订单 {order_id} 的{modification.strip()}已修改成功。"
    except ValueError:
        return "参数格式错误，请使用：订单ID,修改内容"


def query_order_status(order_id: str) -> str:
    """查询订单状态，参数：订单ID"""
    statuses = ["已支付", "已发货", "已签收", "已取消"]  # 移除未支付状态
    status = statuses[hash(order_id) % len(statuses)]
    return f"订单 {order_id} 当前状态：{status}"


def logistics_query(order_id: str) -> str:
    """查询物流信息，参数：订单ID"""
    status = query_order_status(order_id).split("：")[-1]
    logistics_info = {
        "已发货": f"订单 {order_id} 的物流信息：快递单号 KDS982734，正在运输中，预计明天送达。",
        "已签收": f"订单 {order_id} 已于 2025年7月1日 15:30 签收，签收人：李小明。",
    }
    return logistics_info.get(status, f"订单 {order_id} 当前状态为 {status}，暂无物流信息。")


def refund_order(order_id: str) -> str:
    """取消订单并退款，参数：订单ID"""
    status = query_order_status(order_id).split("：")[-1]
    if status in ["已取消", "已签收"]:
        return f"订单 {order_id} 当前状态为 {status}，无法办理退款。"
    return f"订单 {order_id} 已成功取消，退款将在3-5个工作日内退回原支付账户。"


def get_tools():
    """获取所有工具列表"""
    return [
        Tool(
            name="CreateOrder",
            func=create_order,
            description="创建新订单，参数格式：商品名称,数量,收货地址,支付方式"
        ),
        Tool(
            name="ModifyOrder",
            func=modify_order,
            description="修改订单信息，参数格式：订单ID,修改内容（如：收货地址=北京市朝阳区）"
        ),
        Tool(
            name="QueryOrderStatus",
            func=query_order_status,
            description="查询订单状态，参数：订单ID"
        ),
        Tool(
            name="LogisticsQuery",
            func=logistics_query,
            description="查询物流信息，参数：订单ID"
        ),
        Tool(
            name="RefundOrder",
            func=refund_order,
            description="取消订单并退款，参数：订单ID"
        )
    ]