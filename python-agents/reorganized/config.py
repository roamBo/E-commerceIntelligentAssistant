# config.py
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件

class Config:
    # LangChain LLM 配置
    LLM_MODEL_NAME: str = os.environ.get("LLM_MODEL_NAME", "deepseek-ai/DeepSeek-R1")
    LLM_TEMPERATURE: float = float(os.environ.get("LLM_TEMPERATURE", 0.1))
    SILICONFLOW_API_KEY: str = os.environ.get("SILICONFLOW_API_KEY")
    SILICONFLOW_API_BASE: str = os.environ.get("SILICONFLOW_API_BASE", "https://api.siliconflow.cn/v1" )

    # Redis 配置
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # 外部商品 API 配置 (可选)
    PRODUCT_API_BASE_URL: Optional[str] = os.environ.get("PRODUCT_API_BASE_URL")
    # 根据 PRODUCT_API_BASE_URL 是否设置来决定是否使用外部API
    USE_EXTERNAL_PRODUCT_API: bool = bool(PRODUCT_API_BASE_URL)

    # ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

    # 验证配置
    @classmethod
    def validate(cls):
        if not cls.SILICONFLOW_API_KEY:
            raise ValueError("SILICONFLOW_API_KEY 环境变量未设置。")
        if not cls.REDIS_URL:
            raise ValueError("REDIS_URL 环境变量未设置。")
        # 如果使用外部API，则 PRODUCT_API_BASE_URL 必须设置
        if cls.USE_EXTERNAL_PRODUCT_API and not cls.PRODUCT_API_BASE_URL:
            raise ValueError("PRODUCT_API_BASE_URL 环境变量未设置，但 USE_EXTERNAL_PRODUCT_API 为 True。")

# 在应用启动时调用验证
Config.validate()
