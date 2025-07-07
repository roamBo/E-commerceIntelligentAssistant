# main.py
import nest_asyncio

nest_asyncio.apply()  # 解决 asyncio.run() 错误

import os
from typing import Dict, Any
from urllib.parse import urlparse
from contextlib import asynccontextmanager

import uvicorn
import redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from models import ChatRequest, ChatResponse  # 导入API模型
from agent import get_agent_executor  # 导入获取AgentExecutor的函数

# 【条件导入】如果使用外部API，则导入 ProductAPIClient
if Config.USE_EXTERNAL_PRODUCT_API:
    from services.product_api_client import get_product_api_client


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
        print(f"✅ API 启动成功，并成功连接到 Redis 服务器: {Config.REDIS_URL}")
    except Exception as e:
        raise RuntimeError(f"❌ API 启动失败：无法连接到 Redis 服务器: {Config.REDIS_URL}. 错误详情: {e}")

    # 【修改】根据配置决定是否连接外部商品 API
    if Config.USE_EXTERNAL_PRODUCT_API:
        try:
            product_client = await get_product_api_client()
            # 尝试调用一个简单的API，例如查询所有可用商品，以验证连接
            await product_client.search_available_products()
            print(f"✅ 成功连接到商品 API: {Config.PRODUCT_API_BASE_URL}")
        except Exception as e:
            raise RuntimeError(f"❌ API 启动失败：无法连接到商品 API: {Config.PRODUCT_API_BASE_URL}. 错误详情: {e}")
    else:
        print("ℹ️ 未配置 PRODUCT_API_BASE_URL，将使用硬编码商品数据。")

    yield  # 在这里，应用开始处理请求

    # 应用关闭时执行的代码
    if Config.USE_EXTERNAL_PRODUCT_API:
        product_client = await get_product_api_client()
        await product_client.close()
        print("--- Product API Client closed ---")
    print("--- Application shutdown complete ---")


app = FastAPI(
    title="商品推荐 Agent API",
    description="提供基于 LangChain Agent 的商品推荐服务，支持多轮对话记忆。",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
origins = [
    "http://localhost",
    "http://localhost:5173",  # Vue 前端开发服务器的地址
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
        agent_executor = get_agent_executor(session_id)

        # 调用 AgentExecutor
        response = await agent_executor.ainvoke({"input": user_input, "chat_history": []})
        final_report = response['output']

        return ChatResponse(response=final_report, session_id=session_id)

    except Exception as e:
        print(f"处理请求时发生错误 (Session ID: {session_id}): {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {e}")


# --- 运行 FastAPI 应用 ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
