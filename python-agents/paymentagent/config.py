# config.py - 配置文件
import os
from dataclasses import dataclass

@dataclass
class PaymentConfig:
    """支付代理配置类"""

    # 硅基流动API配置
    SILICONFLOW_API_KEY: str = os.getenv("SILICONFLOW_API_KEY", "")
    SILICONFLOW_BASE_URL: str = "https://api.siliconflow.cn/v1"

    # DeepSeek模型配置
    MODEL_NAME: str = "deepseek-chat"
    MODEL_TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 2000

    # 支付限制配置
    MAX_PAYMENT_AMOUNT: float = 10000.0
    SUPPORTED_CURRENCIES: list = None
    SUPPORTED_PAYMENT_METHODS: list = None

    def __post_init__(self):
        if self.SUPPORTED_CURRENCIES is None:
            self.SUPPORTED_CURRENCIES = ['CNY', 'USD', 'EUR']

        if self.SUPPORTED_PAYMENT_METHODS is None:
            self.SUPPORTED_PAYMENT_METHODS = ['alipay', 'wechat', 'bank_card', 'paypal']

        if not self.SILICONFLOW_API_KEY:
            raise ValueError("SILICONFLOW_API_KEY environment variable is required")