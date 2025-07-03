# app_config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # 模型配置
    API_KEY: str = os.getenv("API_KEY", "")
    API_URL: str = os.getenv("API_URL", "https://api.siliconflow.cn/v1")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-R1")

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 聊天历史文件配置
    CHAT_HISTORY_DIR: str = os.path.join(os.getcwd(), 'data')
    CHAT_HISTORY_FILE: str = os.path.join(CHAT_HISTORY_DIR, 'chat_history.json')


settings = Settings()