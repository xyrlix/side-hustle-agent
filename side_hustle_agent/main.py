"""
副业雷达 —— 主入口
"""

import os
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

import time
from collections import defaultdict
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .api.routes import router

# 禁用所有第三方 logger 的默认输出
for _logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "httpx", "httpcore"]:
    _log = logging.getLogger(_logger_name)
    _log.setLevel(logging.WARNING)
    _log.propagate = False

# 应用日志：只用一个 handler，格式精简
app_logger = logging.getLogger("side_hustle_agent")
app_logger.setLevel(logging.INFO)
app_logger.propagate = False
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s │ %(levelname)s │ %(message)s",
    datefmt="%H:%M:%S",
))
app_logger.handlers.clear()
app_logger.addHandler(_handler)


app = FastAPI(
    title="副业雷达",
    description="基于多智能体协同的个性化轻创业推荐系统",
    version="0.1.0",
)

# CORS - 生产环境应配置具体域名
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 信任的Host（防止HTTP Host头攻击）
TRUSTED_HOSTS = os.getenv("TRUSTED_HOSTS", "*").split(",")
if TRUSTED_HOSTS != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的请求限流中间件"""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # 清理过期记录
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if now - t < self.window_seconds
        ]

        # 检查限流
        if len(self.requests[client_ip]) >= self.max_requests:
            return Response(
                content='{"detail":"请求过于频繁，请稍后再试"}',
                status_code=429,
                media_type="application/json"
            )

        self.requests[client_ip].append(now)
        return await call_next(request)


# 添加限流中间件
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

app.include_router(router)


@app.get("/")
async def root():
    return {"name": "副业雷达", "version": "0.1.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    app_logger.info(f"{request.method} {request.url.path} → {response.status_code}")
    return response


def main():
    import uvicorn

    # 启动调度器
    from .scheduler import start_scheduler
    scheduler_interval = int(os.getenv("SCHEDULER_INTERVAL", "60"))
    if scheduler_interval > 0:
        start_scheduler(interval=scheduler_interval)

    port = int(os.getenv("PORT", "8000"))
    app_logger.info(f"启动副业雷达 · 端口 {port}")
    uvicorn.run(
        "side_hustle_agent.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
