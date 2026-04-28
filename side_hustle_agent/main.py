"""
副业雷达 —— 主入口
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="副业雷达",
    description="基于多智能体协同的个性化轻创业推荐系统",
    version="0.1.0",
)

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
    uvicorn.run("side_hustle_agent.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
