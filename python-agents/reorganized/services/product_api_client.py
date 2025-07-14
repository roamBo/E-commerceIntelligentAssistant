# services/product_api_client.py
import httpx
import json
import asyncio  # 【新增】用于异步化 requests
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin  # 用于拼接URL

from config import Config
from models import Product  # 导入Product模型


class ProductAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> List[Product]:
        """通用请求方法"""
        full_url = urljoin(self.base_url, endpoint)
        print(f"--- Calling Product API: {method.upper()} {full_url} with params: {params} ---")
        print(f"Actual request URL: {self.client.build_request(method, full_url, params=params).url}")
        try:
            response = await self.client.request(method, full_url, params=params, timeout=10)
            response.raise_for_status()  # 检查HTTP错误状态码
            data = response.json()

            # 假设API返回的是一个列表，或者包含一个"products"键的字典
            if isinstance(data, dict) and "products" in data:
                data = data["products"]
            elif not isinstance(data, list):
                # 如果返回的不是列表，可能是单个商品或错误，尝试包装成列表
                data = [data] if data else []

            # 将字典列表转换为 Product 模型的列表
            return [Product(**item) for item in data]

        except httpx.HTTPStatusError as e:
            print(f"Product API HTTP Error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"商品API请求失败: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Product API Request Error: {e}")
            raise ValueError(f"商品API请求失败: {e}")
        except json.JSONDecodeError:
            print(f"Product API returned invalid JSON: {response.text}")
            raise ValueError("商品API返回数据格式错误")
        except Exception as e:
            print(f"Product API Unknown Error: {e}")
            raise ValueError(f"商品API未知错误: {e}")

    async def search_by_name(self, name: str) -> List[Product]:
        return await self._request("GET", "/product/api/products/search", {"name": name})

    async def search_by_category(self, category: str) -> List[Product]:
        return await self._request("GET", f"/product/api/products/category/{category}")

    async def search_by_brand(self, brand: str) -> List[Product]:
        return await self._request("GET", f"/product/api/products/brand/{brand}")

    async def search_by_price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[
        Product]:
        params = {}
        if min_price is not None:
            params["minPrice"] = min_price
        if max_price is not None:
            params["maxPrice"] = max_price
        return await self._request("GET", "/product/api/products/price-range", params)

    async def search_by_tag(self, tag: str) -> List[Product]:
        return await self._request("GET", f"/product/api/products/tag/{tag}")

    async def search_available_products(self) -> List[Product]:
        return await self._request("GET", "/product/api/products/available")

    async def close(self):
        """关闭 httpx 客户端会话"""
        await self.client.aclose()


# 全局客户端实例，在应用启动时初始化
product_api_client: Optional[ProductAPIClient] = None


async def get_product_api_client() -> ProductAPIClient:
    """获取全局 ProductAPIClient 实例"""
    global product_api_client
    if product_api_client is None:
        product_api_client = ProductAPIClient(Config.PRODUCT_API_BASE_URL)
    return product_api_client
