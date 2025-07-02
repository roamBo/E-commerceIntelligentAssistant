# core/tools.py（修复 Pydantic 2.x 类型注解问题）
from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field


class CreateOrderInput(BaseModel):
    """创建订单的输入参数"""
    product_name: str = Field(..., description="商品名称")
    quantity: int = Field(..., description="商品数量")
    address: str = Field(..., description="收货地址")
    payment_method: str = Field(..., description="支付方式，如微信、支付宝、银行卡")


class CreateOrderTool(BaseTool):
    name: str = "CreateOrder"  # 添加类型注解
    description: str = "创建新订单，需要提供商品信息、收货地址和支付方式"  # 添加类型注解
    args_schema: Type[CreateOrderInput] = CreateOrderInput  # 添加类型注解

    def _run(self, product_name: str, quantity: int, address: str, payment_method: str) -> str:
        order_id = f"ORD-{hash(product_name + address) % 1000000:06d}"
        return (f"已成功创建订单 {order_id}：\n"
                f"- 商品: {product_name} x {quantity}\n"
                f"- 收货地址: {address}\n"
                f"- 支付方式: {payment_method}\n\n"
                "你可以使用订单ID查询订单状态或物流信息。")

    async def _arun(self, product_name: str, quantity: int, address: str, payment_method: str) -> str:
        return self._run(product_name, quantity, address, payment_method)


class ModifyOrderInput(BaseModel):
    """修改订单的输入参数"""
    order_id: str = Field(..., description="需要修改的订单ID")
    field_to_modify: str = Field(..., description="要修改的字段，如address、quantity等")
    new_value: str = Field(..., description="新的值")


class ModifyOrderTool(BaseTool):
    name: str = "ModifyOrder"  # 添加类型注解
    description: str = "修改现有订单信息，需要提供订单ID、要修改的字段和新值"  # 添加类型注解
    args_schema: Type[ModifyOrderInput] = ModifyOrderInput  # 添加类型注解

    def _run(self, order_id: str, field_to_modify: str, new_value: str) -> str:
        return f"订单 {order_id} 的 {field_to_modify} 已修改为: {new_value}"

    async def _arun(self, order_id: str, field_to_modify: str, new_value: str) -> str:
        return self._run(order_id, field_to_modify, new_value)


class QueryOrderStatusInput(BaseModel):
    """查询订单状态的输入参数"""
    order_id: str = Field(..., description="需要查询的订单ID")


class QueryOrderStatusTool(BaseTool):
    name: str = "QueryOrderStatus"  # 添加类型注解
    description: str = "查询订单当前状态，需要提供订单ID"  # 添加类型注解
    args_schema: Type[QueryOrderStatusInput] = QueryOrderStatusInput  # 添加类型注解

    def _run(self, order_id: str) -> str:
        status_map = {
            "ORD-123456": "已发货，物流单号: SF1234567890",
            "ORD-234567": "处理中，等待支付确认",
            "ORD-345678": "已送达，签收人: 李先生"
        }
        status = status_map.get(order_id, "未找到该订单，请检查订单ID是否正确")
        return f"订单 {order_id} 的当前状态: {status}"

    async def _arun(self, order_id: str) -> str:
        return self._run(order_id)


class RefundOrderInput(BaseModel):
    """退款订单的输入参数"""
    order_id: str = Field(..., description="需要退款的订单ID")
    reason: Optional[str] = Field(None, description="退款原因")


class RefundOrderTool(BaseTool):
    name: str = "RefundOrder"  # 添加类型注解
    description: str = "取消订单并申请退款，需要提供订单ID和可选的退款原因"  # 添加类型注解
    args_schema: Type[RefundOrderInput] = RefundOrderInput  # 添加类型注解

    def _run(self, order_id: str, reason: str = "用户取消订单") -> str:
        return (f"订单 {order_id} 的退款申请已提交。\n"
                f"- 退款原因: {reason}\n"
                f"- 退款编号: REF-{order_id[4:]}\n"
                f"退款将在3-5个工作日内退回原支付账户。")

    async def _arun(self, order_id: str, reason: str = "用户取消订单") -> str:
        return self._run(order_id, reason)


class LogisticsQueryInput(BaseModel):
    """查询物流的输入参数"""
    order_id: str = Field(..., description="需要查询物流的订单ID")


class LogisticsQueryTool(BaseTool):
    name: str = "LogisticsQuery"  # 添加类型注解
    description: str = "查询订单的物流信息，需要提供订单ID"  # 添加类型注解
    args_schema: Type[LogisticsQueryInput] = LogisticsQueryInput  # 添加类型注解

    def _run(self, order_id: str) -> str:
        logistics_map = {
            "ORD-123456": ("物流公司: 顺丰速运\n"
                           "物流单号: SF1234567890\n"
                           "最新状态: 2023-10-15 10:30 已到达北京市朝阳区派送点\n"
                           "预计送达时间: 今天 18:00前"),
            "ORD-234567": "订单尚未发货，暂无法查询物流信息",
            "ORD-345678": "订单已完成配送，无需查询物流信息"
        }
        info = logistics_map.get(order_id, "未找到该订单的物流信息，请检查订单ID是否正确")
        return f"订单 {order_id} 的物流信息:\n{info}"

    async def _arun(self, order_id: str) -> str:
        return self._run(order_id)


def get_tools():
    """获取所有可用工具"""
    return [
        CreateOrderTool(),
        ModifyOrderTool(),
        QueryOrderStatusTool(),
        RefundOrderTool(),
        LogisticsQueryTool()
    ]