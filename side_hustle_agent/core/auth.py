"""
认证中间件
"""

from functools import wraps
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .database import verify_token, check_user_permission, get_user_by_id

security = HTTPBearer(auto_error=False)


async def get_current_user(request: Request) -> dict | None:
    """从请求中获取当前用户"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    user_data = verify_token(token)
    if user_data:
        # 补充用户完整信息
        full_user = get_user_by_id(user_data["user_id"])
        if full_user:
            user_data["user"] = full_user
    return user_data


async def require_auth(request: Request) -> dict:
    """要求用户已认证"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    return user


async def require_admin(request: Request) -> dict:
    """要求管理员权限"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


def require_permission(permission: str):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从 kwargs 中获取 request
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if not request:
                raise HTTPException(status_code=500, detail="无法获取请求")

            user = await get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="请先登录")

            # 检查权限
            if not check_user_permission(user["user_id"], permission):
                raise HTTPException(status_code=403, detail=f"需要权限: {permission}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator