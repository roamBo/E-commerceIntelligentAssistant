# tools.py
import json
from typing import List, Optional, Dict, Any

from langchain_core.tools import tool

from config import Config
from models import FinalResponse, Recommendation
from data.product_db import get_products_from_db

if Config.USE_EXTERNAL_PRODUCT_API:
    from services.product_api_client import get_product_api_client


@tool
async def search_products(input_str: str) -> str:
    """
    根据多种条件搜索商品数据库。输入应为JSON字符串，包含以下可选参数:
    - name: 商品名称关键词
    - category: 商品分类
    - brand: 商品品牌
    - min_price: 最小价格
    - max_price: 最大价格
    - tag: 商品标签
    - available_only: 是否只查询有库存的商品
    - query: 通用查询字符串
    """
    try:
        # 解析JSON输入字符串
        params = json.loads(input_str)
    except json.JSONDecodeError:
        return json.dumps({"error": "输入参数不是有效的JSON格式"})

    # 从字典中提取参数
    name = params.get("name")
    category = params.get("category")
    brand = params.get("brand")
    min_price = params.get("min_price")
    max_price = params.get("max_price")
    tag = params.get("tag")
    available_only = params.get("available_only", False)
    query = params.get("query")

    print(
        f"--- 调用工具: search_products(name={name}, category={category}, brand={brand}, min_price={min_price}, max_price={max_price}, tag={tag}, available_only={available_only}, query={query}) ---")

    products = []
    try:
        if Config.USE_EXTERNAL_PRODUCT_API:
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
            elif query:
                products = await product_client.search_by_name(query)
            else:
                return json.dumps({"error": "请提供至少一个搜索条件。"})

            product_dicts = [p.dict() for p in products[:3]]

        else:
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
            elif query:
                products = get_products_from_db(name=query)
            else:
                return json.dumps({"error": "请提供至少一个搜索条件。"})

            product_dicts = products[:3]

        return json.dumps(product_dicts, ensure_ascii=False)

    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"工具内部未知错误: {e}"})


@tool(args_schema=FinalResponse)
def format_final_response(demand_analysis: str, search_keyword: str,
                          recommendations: List[Recommendation]) -> FinalResponse:
    print("--- 调用工具: format_final_response ---")
    return FinalResponse(
        demand_analysis=demand_analysis,
        search_keyword=search_keyword,
        recommendations=recommendations
    )