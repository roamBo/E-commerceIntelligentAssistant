# config.py - 配置文件
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

@dataclass
class PaymentConfig:
    """支付代理配置类"""

    # 硅基流动API配置
    SILICONFLOW_API_KEY: str = os.getenv("SILICONFLOW_API_KEY", "")
    SILICONFLOW_BASE_URL: str = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

    # DeepSeek模型配置
    MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-R1")
    MODEL_TEMPERATURE: float = float(os.getenv("MODEL_TEMPERATURE", "0.1"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))

    # 支付限制配置
    MAX_PAYMENT_AMOUNT: float = float(os.getenv("MAX_PAYMENT_AMOUNT", "10000.0"))
    SUPPORTED_CURRENCIES: list = None
    SUPPORTED_PAYMENT_METHODS: list = None

    def __post_init__(self):
        if self.SUPPORTED_CURRENCIES is None:
            currencies_str = os.getenv("SUPPORTED_CURRENCIES", "CNY,USD,EUR")
            self.SUPPORTED_CURRENCIES = [c.strip() for c in currencies_str.split(",")]

        if self.SUPPORTED_PAYMENT_METHODS is None:
            methods_str = os.getenv("SUPPORTED_PAYMENT_METHODS", "alipay,wechat,bank_card,paypal")
            self.SUPPORTED_PAYMENT_METHODS = [m.strip() for m in methods_str.split(",")]

        if not self.SILICONFLOW_API_KEY:
            raise ValueError("SILICONFLOW_API_KEY environment variable is required")