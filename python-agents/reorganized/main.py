# main.py
import nest_asyncio
nest_asyncio.apply() # 解决 asyncio.run() 错误

import os
from typing import Dict, Any
from urllib.parse import urlparse
from contextlib import asynccontextmanager
import logging # 【新增】日志
import redis # 【新增】Redis 客户端用于测试连接

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from models import ChatRequest, ChatResponse # 导入API模型
from supervisor_agent import get_multi_agent_workflow # 【修改】导入多 Agent 工作流

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI 应用实例 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行的代码
    try:
        Config.validate()
    except ValueError as e:
        raise RuntimeError(f"配置错误: {e}")

    # 尝试连接 Redis
    try:
        parsed_url = urlparse(Config.REDIS_URL)
        test_client = redis.Redis(
            host=parsed_url.hostname,
            port=parsed_url.port,
            db=int(parsed_url.path.lstrip('/')) if parsed_url.path else 0,
            password=parsed_url.password if parsed_url.password else None
        )
        test_client.ping()
        logger.info(f"✅ API 启动成功，并成功连接到 Redis 服务器: {Config.REDIS_URL}")
    except Exception as e:
        raise RuntimeError(f"❌ API 启动失败：无法连接到 Redis 服务器: {Config.REDIS_URL}. 错误详情: {e}")

    # 根据配置决定是否连接外部商品 API
    if Config.USE_EXTERNAL_PRODUCT_API:
        try:
            from services.product_api_client import get_product_api_client
            product_client = await get_product_api_client()
            # 尝试调用一个简单的API，例如查询所有可用商品，以验证连接
            await product_client.search_available_products()
            logger.info(f"✅ 成功连接到商品 API: {Config.PRODUCT_API_BASE_URL}")
        except Exception as e:
            raise RuntimeError(f"❌ API 启动失败：无法连接到商品 API: {Config.PRODUCT_API_BASE_URL}. 错误详情: {e}")
    else:
        logger.info("ℹ️ 未配置 PRODUCT_API_BASE_URL，将使用硬编码商品数据。")

    # 【修改】初始化多 Agent 工作流
    await get_multi_agent_workflow()
    logger.info("多 Agent 工作流初始化完成。")

    yield # 在这里，应用开始处理请求

    # 应用关闭时执行的代码
    if Config.USE_EXTERNAL_PRODUCT_API:
        from services.product_api_client import get_product_api_client
        product_client = await get_product_api_client()
        await product_client.close()
        logger.info("--- Product API Client closed ---")
    logger.info("--- Application shutdown complete ---")


app = FastAPI(
    title="多 Agent 智能服务 API",
    description="提供基于 LangGraph 监管者模式的多领域智能服务。",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
origins = [
    "http://localhost",
    "http://localhost:5173", # Vue 前端开发服务器的地址
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

# --- API 端点 ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_input = request.user_input

    try:
        # 【修改】通过 get_multi_agent_workflow() 获取实例，并调用其 invoke_workflow 方法
        workflow = await get_multi_agent_workflow()
        final_response_text = await workflow.invoke_workflow(user_input, session_id)

        return ChatResponse(response=final_response_text, session_id=session_id)

    except Exception as e:
        logger.error(f"处理请求时发生错误 (Session ID: {session_id}): {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {e}")

# --- 运行 FastAPI 应用 ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) # 端口改为 8000，避免与之前 8085 冲突
