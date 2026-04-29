"""
副业雷达 —— 主入口
"""

import os
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import router
from .core.config import get_settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("side_hustle_agent")

settings = get_settings()

app = FastAPI(
    title="副业雷达",
    description="基于多智能体协同的个性化轻创业推荐系统",
    version="0.1.0",
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"  → {response.status_code}")
    return response

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.get("/")
async def root():
    """健康检查"""
    return {
        "name": "副业雷达",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


def main():
    """启动服务"""
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"启动副业雷达服务，端口: {port}")
    uvicorn.run(
        "side_hustle_agent.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()