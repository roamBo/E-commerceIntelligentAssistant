import asyncio
import json
from config import Config
from tools import search_products


async def test_product_search():
    test_cases = [
        {"name": "蓝牙耳机"},
        {"category": "smartphone", "min_price": 3000, "max_price": 5000},
        {"brand": "AudioTech", "available_only": True},
        {"query": "游戏笔记本"}
    ]

    if not Config.USE_EXTERNAL_PRODUCT_API:
        print("⚠️ 未配置外部API，测试将使用硬编码数据")
    else:
        print(f"✅ 使用外部API: {Config.PRODUCT_API_BASE_URL}")

    for i, params in enumerate(test_cases, 1):
        print(f"\n🔍 测试用例 #{i}: {params}")

        try:
            # 1. 将参数字典转换为JSON字符串
            tool_input = json.dumps(params)
            print(tool_input)

            # 2. 使用.arun()方法异步执行工具
            result = await search_products.arun(tool_input)

            # 3. 解析并验证结果
            try:
                data = json.loads(result)
            except json.JSONDecodeError:
                print(f"❌ 返回结果不是有效JSON: {result}")
                continue

            if isinstance(data, list) and len(data) > 0:
                print(f"✅ 搜索成功，返回 {len(data)} 条结果")
                print("第一条结果:", json.dumps(data[0], indent=2, ensure_ascii=False))
            elif isinstance(data, dict) and "error" in data:
                print(f"❌ 搜索失败: {data['error']}")
            else:
                print("⚠️ 未找到匹配商品")

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")


if __name__ == "__main__":
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        exit(1)

    asyncio.run(test_product_search())