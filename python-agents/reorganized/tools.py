# tools.py
import json
from typing import List, Optional

from langchain_core.tools import tool

from config import Config  # 导入配置
from models import FinalResponse, Recommendation  # 导入模型
from data.product_db import get_products_from_db  # 导入硬编码数据库查询函数

# 【条件导入】如果使用外部API，则导入 ProductAPIClient
if Config.USE_EXTERNAL_PRODUCT_API:
    from services.product_api_client import get_product_api_client


# 【重构】search_products 工具，现在它将根据配置选择数据源
@tool
async def search_products(
        name: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        tag: Optional[str] = None,
        available_only: Optional[bool] = False,
        query: Optional[str] = None  # 用于接收通用查询，Agent会尝试解析为上述参数
) -> str:
    """
    根据多种条件搜索商品数据库。此工具会根据配置选择查询硬编码数据或外部API。
    你可以通过名称、分类、品牌、价格范围、标签或只查询有库存的商品。
    如果提供了通用查询，Agent会尝试从中提取上述参数。

    参数:
    - name (str, optional): 商品名称关键词。
    - category (str, optional): 商品分类。
    - brand (str, optional): 商品品牌。
    - min_price (float, optional): 最小价格。
    - max_price (float, optional): 最大价格。
    - tag (str, optional): 商品标签。
    - available_only (bool, optional): 是否只查询有库存的商品。
    - query (str, optional): 通用查询字符串，Agent会尝试从中提取上述参数。
    """
    print(
        f"--- 调用工具: search_products(name={name}, category={category}, brand={brand}, min_price={min_price}, max_price={max_price}, tag={tag}, available_only={available_only}, query={query}) ---")

    products = []
    try:
        if Config.USE_EXTERNAL_PRODUCT_API:
            # --- 使用外部 API ---
            product_client = await get_product_api_client()

            if name:
                products = await product_client.search_by_name(name)
            elif category:
                products = await product_client.search_by_category(category)
            elif brand:
                products = await product_client.search_by_brand(brand)
            elif tag:
                products = await product_client.search_by_tag(tag)
            elif available_only:
                products = await product_client.search_available_products()
            elif min_price is not None or max_price is not None:
                products = await product_client.search_by_price_range(min_price, max_price)
            elif query:  # 如果有通用查询，尝试解析
                products = await product_client.search_by_name(query)  # 默认按名称搜索
            else:
                return json.dumps({"error": "请提供至少一个搜索条件。"})

            # 将 Product 模型列表转换为字典列表
            product_dicts = [p.dict() for p in products[:3]]

        else:
            # --- 使用硬编码数据库 ---
            print("--- 使用硬编码商品数据库进行查询 ---")
            if name:
                products = get_products_from_db(name=name)
            elif category:
                products = get_products_from_db(category=category)
            elif brand:
                products = get_products_from_db(brand=brand)
            elif tag:
                products = get_products_from_db(tag=tag)
            elif available_only:
                products = get_products_from_db(available_only=True)
            elif min_price is not None or max_price is not None:
                products = get_products_from_db(min_price=min_price, max_price=max_price)
            elif query:  # 如果有通用查询，尝试解析
                products = get_products_from_db(name=query)  # 默认按名称搜索
            else:
                return json.dumps({"error": "请提供至少一个搜索条件。"})

            product_dicts = products[:3]  # 硬编码数据已经是字典列表

        # 返回前3个商品，并转换为JSON字符串
        return json.dumps(product_dicts, ensure_ascii=False)

    except ValueError as e:  # 捕获 ProductAPIClient 抛出的错误
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"工具内部未知错误: {e}"})


@tool(args_schema=FinalResponse)
def format_final_response(demand_analysis: str, search_keyword: str,
                          recommendations: List[Recommendation]) -> FinalResponse:
    """
    当所有信息都收集完毕后，调用此工具来格式化并给出最终的推荐答案。这是整个流程的最后一步。
    """
    print("--- 调用工具: format_final_response ---")
    return FinalResponse(
        demand_analysis=demand_analysis,
        search_keyword=search_keyword,
        recommendations=recommendations
    )
