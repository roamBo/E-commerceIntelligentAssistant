# data/product_db.py
from typing import List, Dict, Any, Optional

PRODUCT_DATABASE: List[Dict[str, Any]] = [
    # 蓝牙耳机分类
    {"id": 1, "name": "无线蓝牙耳机", "price": 299, "brand": "SoundMax", "features": "主动降噪", "category": "headphones"},
    {"id": 2, "name": "运动蓝牙耳机", "price": 399, "brand": "SportPro", "features": "IPX7防水", "category": "headphones"},
    {"id": 4, "name": "降噪无线耳机", "price": 599, "brand": "AudioTech", "features": "HiFi音质", "category": "headphones"},
    {"id": 5, "name": "入耳式蓝牙耳机", "price": 199, "brand": "BassBoost", "features": "重低音效果", "category": "headphones"},

    # 智能手表分类
    {"id": 3, "name": "智能手表", "price": 899, "brand": "TechGiant", "features": "健康监测", "category": "smartwatch"},
    {"id": 6, "name": "运动智能手表", "price": 699, "brand": "FitTrack", "features": "GPS定位", "category": "smartwatch"},
    {"id": 7, "name": "商务智能手表", "price": 1299, "brand": "LuxWatch", "features": "皮质表带", "category": "smartwatch"},

    # 智能手机分类
    {"id": 8, "name": "旗舰智能手机", "price": 5999, "brand": "PhonePro", "features": "5G网络", "category": "smartphone"},
    {"id": 9, "name": "中端智能手机", "price": 2999, "brand": "BudgetPhone", "features": "大容量电池", "category": "smartphone"},
    {"id": 10, "name": "轻薄智能手机", "price": 4299, "brand": "SlimTech", "features": "OLED屏幕", "category": "smartphone"},

    # 笔记本电脑分类
    {"id": 11, "name": "商务笔记本", "price": 7999, "brand": "BusinessPro", "features": "长续航", "category": "laptop"},
    {"id": 12, "name": "游戏笔记本", "price": 12999, "brand": "GameMaster", "features": "RTX显卡", "category": "laptop"},
    {"id": 13, "name": "轻薄笔记本", "price": 5499, "brand": "UltraThin", "features": "金属机身", "category": "laptop"},

    # 平板电脑分类
    {"id": 14, "name": "旗舰平板电脑", "price": 4999, "brand": "TabletPro", "features": "高刷新率屏幕", "category": "tablet"},
    {"id": 15, "name": "教育平板电脑", "price": 2299, "brand": "EduTablet", "features": "护眼屏幕", "category": "tablet"},
    {"id": 16, "name": "迷你平板电脑", "price": 1899, "brand": "MiniTab", "features": "便携设计", "category": "tablet"},

    # 智能音箱分类
    {"id": 17, "name": "智能音箱", "price": 349, "brand": "VoiceAssistant", "features": "语音控制", "category": "speaker"},
    {"id": 18, "name": "防水智能音箱", "price": 499, "brand": "PoolSound", "features": "户外使用", "category": "speaker"},
    {"id": 19, "name": "高保真智能音箱", "price": 899, "brand": "MusicMaster", "features": "3D环绕声", "category": "speaker"},
]

def get_products_from_db(
    name: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    tag: Optional[str] = None, # 硬编码数据中没有tag，这里仅作接口兼容
    available_only: Optional[bool] = False # 硬编码数据中所有商品都视为available
) -> List[Dict[str, Any]]:
    """
    从硬编码的商品数据库中查询商品。
    """
    results = []
    for p in PRODUCT_DATABASE:
        match = True
        if name and name.lower() not in p["name"].lower():
            match = False
        if category and category.lower() != p["category"].lower():
            match = False
        if brand and brand.lower() != p["brand"].lower():
            match = False
        if min_price is not None and p["price"] < min_price:
            match = False
        if max_price is not None and p["price"] > max_price:
            match = False
        # 硬编码数据没有tag和available_only的复杂逻辑，这里简化处理
        # if tag and tag.lower() not in [t.lower() for t in p.get("tags", [])]:
        #     match = False
        # if available_only and p.get("stock", 0) <= 0:
        #     match = False

        if match:
            results.append(p)
    return results
