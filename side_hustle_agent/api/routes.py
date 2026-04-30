"""
API 路由
"""

import os
import json
from typing import Any

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..core.models import UserInput
from ..core.config import update_runtime_config, get_runtime_config, get_settings
from ..core.auth import get_current_user, require_admin
from ..core.database import (
    init_db, get_user_by_username, get_user_by_id, create_user,
    verify_password, create_token, save_recommendation,
    get_user_recommendations, get_all_users, get_stats,
    create_content, get_content_by_id, get_user_contents, update_content, delete_content,
    get_content_versions, create_campaign, get_user_campaigns, add_content_to_campaign,
    create_platform_account, get_user_platform_accounts, update_platform_account, delete_platform_account,
    create_material, get_user_materials, delete_material,
    create_publish_log, update_publish_log, get_content_publish_logs,
    # RBAC
    get_all_roles, get_all_permissions, get_user_roles, assign_role_to_user,
    get_user_permissions, get_user_by_username,
    # Analytics
    upsert_analytics, get_user_analytics, get_analytics_summary,
    # Scheduled posts
    create_scheduled_post, get_scheduled_posts, cancel_scheduled_post,
)
from ..orchestrator import SideHustleOrchestrator
from ..core.database import get_db

router = APIRouter(prefix="/api", tags=["副业推荐"])


# 初始化数据库
init_db()


# ============ 认证相关 ============

from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = ""


@router.post("/auth/register")
async def register(req: RegisterRequest):
    """用户注册"""
    if not req.username or not req.password:
        return {"success": False, "message": "用户名和密码不能为空"}
    result = create_user(req.username, req.password, req.email)
    if "error" in result:
        return {"success": False, "message": result["error"]}
    token = create_token(result["id"], result["username"], result["role"])
    return {"success": True, "token": token, "user": {"id": result["id"], "username": result["username"], "role": result["role"]}}


@router.post("/auth/login")
async def login(req: LoginRequest):
    """用户登录"""
    user = get_user_by_username(req.username)
    if not user or not verify_password(req.password, user["password_hash"]):
        return {"success": False, "message": "用户名或密码错误"}
    token = create_token(user["id"], user["username"], user["role"])
    return {"success": True, "token": token, "user": {"id": user["id"], "username": user["username"], "role": user["role"]}}


@router.get("/auth/me")
async def get_me(request: Request):
    """获取当前用户信息"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "未登录"}
    full_user = get_user_by_id(user["user_id"])
    return {"success": True, "user": full_user}


# ============ 副业推荐 ============

@router.post("/recommend")
async def recommend_side_hustle(user_input: UserInput, request: Request) -> dict[str, Any]:
    """获取副业推荐（支持游客和登录用户）"""
    # 获取当前用户（如果有）
    current_user = await get_current_user(request)

    orchestrator = SideHustleOrchestrator()
    result = await orchestrator.run(user_input)

    # 如果用户已登录，保存推荐记录
    if current_user and result.get("success"):
        try:
            input_dict = user_input.model_dump()
            result_data = result.get("data", {})
            save_recommendation(current_user["user_id"], input_dict, result_data)
        except:
            pass  # 不影响主流程

    return result


@router.post("/feedback")
async def submit_feedback(
    user_input: UserInput,
    feedback: str,
    reason: str | None = None,
    request: Request = None
) -> dict[str, Any]:
    """提交执行反馈"""
    orchestrator = SideHustleOrchestrator()
    result = await orchestrator.run_with_feedback(user_input, feedback)
    return result


# ============ 配置相关 ============

@router.get("/config")
async def get_config() -> dict[str, Any]:
    """获取当前 LLM 配置（不返回实际 API Key）"""
    config = get_runtime_config()
    provider = config.get("provider") or os.getenv("LLM_PROVIDER", "deepseek")
    model = config.get("model") or os.getenv("LLM_MODEL", "")

    if not model:
        defaults = {
            "deepseek": "deepseek-chat",
            "minimax": "MiniMax-Text-01",
            "qwen": "qwen-turbo",
            "kimi": "moonshot-v1-8k",
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
        }
        model = defaults.get(provider, "deepseek-chat")

    has_api_key = bool(config.get("api_key") or os.getenv(f"{provider.upper()}_API_KEY") or os.getenv("LLM_API_KEY"))

    return {
        "llm_provider": provider,
        "llm_api_key": "********" if has_api_key else "",
        "llm_model": model,
    }


@router.post("/config")
async def save_config(config: dict[str, Any]) -> dict[str, Any]:
    """保存 LLM 配置"""
    provider = config.get("llm_provider", "deepseek")
    api_key = config.get("llm_api_key", "")
    model = config.get("llm_model", "")

    if not api_key:
        return {"success": False, "message": "API Key 不能为空"}

    update_runtime_config(provider, api_key, model)

    return {"success": True, "message": "配置已保存"}


@router.get("/models")
async def get_models(provider: str = "deepseek") -> list[str]:
    """获取指定 Provider 的可用模型列表"""
    models_map = {
        "deepseek": ["deepseek-chat", "deepseek-coder"],
        "qwen": ["qwen-turbo", "qwen-plus", "qwen-max"],
        "kimi": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "minimax": ["MiniMax-Text-01", "abab6.chat"],
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "anthropic": ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-haiku-4-20250514"],
    }
    return models_map.get(provider, ["deepseek-chat"])


# ============ 用户历史记录（需登录）============

@router.get("/history")
async def get_history(request: Request):
    """获取当前用户的推荐历史"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    history = get_user_recommendations(user["user_id"])
    # 解析 JSON 字符串
    for item in history:
        if isinstance(item.get("input_data"), str):
            try:
                item["input_data"] = json.loads(item["input_data"])
            except:
                pass
        if isinstance(item.get("result_data"), str):
            try:
                item["result_data"] = json.loads(item["result_data"])
            except:
                pass
    return {"success": True, "history": history}


# ============ 管理后台（需管理员权限）============

@router.get("/admin/stats")
async def admin_stats(request: Request):
    """获取系统统计"""
    await require_admin(request)
    stats = get_stats()
    return {"success": True, "stats": stats}


@router.get("/admin/users")
async def admin_get_users(request: Request):
    """获取所有用户"""
    await require_admin(request)
    users = get_all_users()
    return {"success": True, "users": users}


@router.get("/admin/recommendations")
async def admin_get_recommendations(request: Request, limit: int = 100):
    """获取所有推荐记录"""
    await require_admin(request)
    conn = get_db()
    import sqlite3
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, input_data, result_data, created_at FROM recommendations ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        item = {"id": row[0], "user_id": row[1], "created_at": row[4]}
        try:
            item["input_data"] = json.loads(row[2].replace("'", '"')) if row[2] else {}
        except:
            item["input_data"] = {}
        try:
            item["result_data"] = json.loads(row[3].replace("'", '"')) if row[3] else {}
        except:
            item["result_data"] = {}
        result.append(item)
    return {"success": True, "recommendations": result}


@router.get("/admin/hustle_stats")
async def admin_hustle_stats(request: Request):
    """获取热门副业统计"""
    await require_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT result_data FROM recommendations")
    rows = cursor.fetchall()
    conn.close()

    # 统计各副业被推荐的次数
    hustle_count: dict[str, int] = {}
    for row in rows:
        try:
            result_data = json.loads(row[0]) if row[0] else {}
            name = result_data.get("selected_recommendation", {}).get("side_hustle", {}).get("name", "")
            if name:
                hustle_count[name] = hustle_count.get(name, 0) + 1
        except:
            pass

    # 排序
    sorted_hustles = sorted(hustle_count.items(), key=lambda x: x[1], reverse=True)
    return {"success": True, "stats": [{"name": name, "count": count} for name, count in sorted_hustles[:10]]}


@router.get("/admin/user_profiles")
async def admin_user_profiles(request: Request):
    """获取用户画像分析"""
    await require_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT input_data FROM recommendations")
    rows = cursor.fetchall()
    conn.close()

    # 统计城市分布
    city_count: dict[str, int] = {}
    # 统计技能分布
    skill_count: dict[str, int] = {}
    # 统计月收入目标分布
    goal_buckets = {"0-3000": 0, "3000-5000": 0, "5000-10000": 0, "10000+": 0}

    for row in rows:
        try:
            input_data = json.loads(row[0]) if row[0] else {}
            city = input_data.get("city", "")
            if city:
                city_count[city] = city_count.get(city, 0) + 1
            skills = input_data.get("skills", [])
            for skill in skills:
                skill_count[skill] = skill_count.get(skill, 0) + 1
            goal = input_data.get("monthly_goal", 0)
            if goal <= 3000:
                goal_buckets["0-3000"] += 1
            elif goal <= 5000:
                goal_buckets["3000-5000"] += 1
            elif goal <= 10000:
                goal_buckets["5000-10000"] += 1
            else:
                goal_buckets["10000+"] += 1
        except:
            pass

    return {
        "success": True,
        "profiles": {
            "city_distribution": sorted(city_count.items(), key=lambda x: x[1], reverse=True)[:10],
            "skill_distribution": sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:15],
            "goal_distribution": goal_buckets,
        }
    }


def get_db():
    """获取数据库连接"""
    from pathlib import Path
    DB_PATH = Path(__file__).parent.parent / "data" / "side_hustle.db"
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================
# 内容管理 API
# ============================================

from pydantic import BaseModel
from datetime import datetime


class ContentCreateRequest(BaseModel):
    title: str
    body: str = ""
    summary: str = ""
    cover_image: str = ""
    tags: list[str] = []
    category: str = ""
    ai_generated: bool = False
    ai_prompt: str = ""


class ContentUpdateRequest(BaseModel):
    title: str | None = None
    body: str | None = None
    summary: str | None = None
    cover_image: str | None = None
    tags: list[str] | None = None
    category: str | None = None
    status: str | None = None
    scheduled_at: str | None = None  # ISO format string


@router.post("/content")
async def create_content_api(request: Request, content: ContentCreateRequest):
    """创建内容"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    result = create_content(user["user_id"], content.title, content.body,
                           content.summary, content.cover_image, content.tags,
                           content.category, content.ai_generated, content.ai_prompt)
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, "content": result}


@router.get("/content/{content_id}")
async def get_content_api(content_id: int, request: Request):
    """获取内容详情"""
    user = await get_current_user(request)
    content = get_content_by_id(content_id, user["user_id"] if user else None)
    if not content:
        return {"success": False, "message": "内容不存在"}
    return {"success": True, "content": content}


@router.get("/content")
async def list_content_api(request: Request, status: str = None, limit: int = 50, offset: int = 0):
    """获取内容列表"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    contents = get_user_contents(user["user_id"], status, limit, offset)
    return {"success": True, "contents": contents, "total": len(contents)}


@router.put("/content/{content_id}")
async def update_content_api(content_id: int, request: Request, update: ContentUpdateRequest):
    """更新内容"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    update_data = update.model_dump(exclude_unset=True)
    if "scheduled_at" in update_data and update_data["scheduled_at"]:
        # 转换 ISO 字符串
        update_data["scheduled_at"] = datetime.fromisoformat(update_data["scheduled_at"].replace("Z", "+00:00"))

    result = update_content(content_id, user["user_id"], **update_data)
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, "content": result}


@router.delete("/content/{content_id}")
async def delete_content_api(content_id: int, request: Request):
    """删除内容"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    result = delete_content(content_id, user["user_id"])
    return {"success": result.get("deleted", False), "message": "删除成功" if result.get("deleted") else "删除失败"}


@router.get("/content/{content_id}/versions")
async def get_content_versions_api(content_id: int, request: Request):
    """获取内容版本历史"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    content = get_content_by_id(content_id, user["user_id"])
    if not content:
        return {"success": False, "message": "内容不存在"}
    versions = get_content_versions(content_id)
    return {"success": True, "versions": versions}


# ============================================
# 活动管理 API
# ============================================

class CampaignCreateRequest(BaseModel):
    name: str
    description: str = ""
    start_date: str | None = None
    end_date: str | None = None


@router.post("/campaigns")
async def create_campaign_api(request: Request, campaign: CampaignCreateRequest):
    """创建活动"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    result = create_campaign(user["user_id"], campaign.name, campaign.description,
                            campaign.start_date, campaign.end_date)
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, "campaign": result}


@router.get("/campaigns")
async def list_campaigns_api(request: Request, limit: int = 50):
    """获取活动列表"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    campaigns = get_user_campaigns(user["user_id"], limit)
    return {"success": True, "campaigns": campaigns}


@router.post("/campaigns/{campaign_id}/content")
async def add_content_to_campaign_api(campaign_id: int, content_id: int, request: Request):
    """添加内容到活动"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    result = add_content_to_campaign(campaign_id, content_id)
    return {"success": True, "result": result}


# ============================================
# 平台账号管理 API
# ============================================

class PlatformAccountCreateRequest(BaseModel):
    platform: str
    account_name: str
    account_id: str = ""
    access_token: str = ""
    refresh_token: str = ""


@router.post("/platforms/accounts")
async def create_platform_account_api(request: Request, account: PlatformAccountCreateRequest):
    """创建平台账号"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    result = create_platform_account(user["user_id"], account.platform, account.account_name,
                                    account.account_id, account.access_token, account.refresh_token)
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, "account": result}


@router.get("/platforms/accounts")
async def list_platform_accounts_api(request: Request):
    """获取平台账号列表"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    accounts = get_user_platform_accounts(user["user_id"])
    return {"success": True, "accounts": accounts}


@router.put("/platforms/accounts/{account_id}")
async def update_platform_account_api(account_id: int, request: Request, followers: int = None, status: str = None):
    """更新平台账号"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    update_data = {}
    if followers is not None:
        update_data["followers"] = followers
    if status is not None:
        update_data["status"] = status
    result = update_platform_account(account_id, user["user_id"], **update_data)
    return {"success": True, "result": result}


@router.delete("/platforms/accounts/{account_id}")
async def delete_platform_account_api(account_id: int, request: Request):
    """删除平台账号"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    result = delete_platform_account(account_id, user["user_id"])
    return {"success": result.get("deleted", False), "message": "删除成功" if result.get("deleted") else "删除失败"}


# ============================================
# 素材管理 API
# ============================================

@router.get("/materials")
async def list_materials_api(request: Request, file_type: str = None, folder: str = None, limit: int = 100):
    """获取素材列表"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    materials = get_user_materials(user["user_id"], file_type, folder, limit)
    return {"success": True, "materials": materials}


@router.delete("/materials/{material_id}")
async def delete_material_api(material_id: int, request: Request):
    """删除素材"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    result = delete_material(material_id, user["user_id"])
    return {"success": result.get("deleted", False), "message": "删除成功" if result.get("deleted") else "删除失败"}


@router.post("/materials/upload")
async def upload_material_api(request: Request):
    """上传素材"""
    from fastapi import UploadFile, File, Form
    from pathlib import Path
    import shutil

    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    try:
        # 解析 multipart form data
        form = await request.form()
        file = form.get("file")
        folder = form.get("folder", "")

        if not file:
            return {"success": False, "message": "没有上传文件"}

        # 确保上传目录存在
        upload_dir = Path(__file__).parent.parent.parent / "data" / "materials" / str(user["user_id"])
        if folder:
            upload_dir = upload_dir / folder
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        filename = file.filename or "unnamed"
        file_path = upload_dir / filename

        # 如果文件已存在，添加时间戳
        if file_path.exists():
            import time
            timestamp = int(time.time())
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
            filename = f"{name}_{timestamp}.{ext}" if ext else f"{name}_{timestamp}"
            file_path = upload_dir / filename

        # 读取并保存文件内容
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 获取文件信息
        file_size = len(content)
        mime_type = file.content_type or "application/octet-stream"

        # 获取图片/视频尺寸
        width = height = 0
        duration = 0

        # 创建素材记录
        material = create_material(
            user_id=user["user_id"],
            filename=filename,
            file_path=str(file_path),
            file_type=mime_type.split("/")[0],
            file_size=file_size,
            mime_type=mime_type,
            width=width,
            height=height,
            duration=duration,
            folder=folder
        )

        return {"success": True, "material": material}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ============================================
# 发布相关 API
# ============================================

@router.post("/content/{content_id}/publish")
async def publish_content_api(content_id: int, platform: str, request: Request):
    """发布内容到指定平台"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    # 验证内容属于当前用户
    content = get_content_by_id(content_id, user["user_id"])
    if not content:
        return {"success": False, "message": "内容不存在"}

    # 创建发布日志
    log = create_publish_log(content_id, platform)

    # TODO: 调用平台 API 实际发布
    # 这里先模拟成功
    update_publish_log(log["id"], "success", published_url=f"https://example.com/{content_id}",
                      published_at=datetime.now().isoformat())

    return {"success": True, "log": log}


@router.get("/content/{content_id}/logs")
async def get_publish_logs_api(content_id: int, request: Request):
    """获取发布日志"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}
    logs = get_content_publish_logs(content_id)
    return {"success": True, "logs": logs}


# ============================================
# 平台信息 API
# ============================================

@router.get("/platforms")
async def get_platforms_api():
    """获取支持的平台列表"""
    platforms = [
        {"id": "wechat_public", "name": "公众号", "content_format": ["text", "image"], "max_content_length": 20000},
        {"id": "toutiao", "name": "头条号", "content_format": ["text", "image", "video"], "max_content_length": 50000},
        {"id": "xiaohongshu", "name": "小红书", "content_format": ["text", "image"], "max_content_length": 10000},
        {"id": "zhihu", "name": "知乎", "content_format": ["text", "image"], "max_content_length": 100000},
        {"id": "baijiahao", "name": "百家号", "content_format": ["text", "image", "video"], "max_content_length": 50000},
        {"id": "bilibili", "name": "B站", "content_format": ["video", "text"], "max_content_length": 50000},
    ]
    return {"success": True, "platforms": platforms}


@router.get("/oauth/{platform}/authorize")
async def oauth_authorize(platform: str, request: Request):
    """获取平台 OAuth 授权 URL"""
    from ..platforms.base import get_platform, get_available_platforms

    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    # 检查平台是否支持 OAuth
    available = get_available_platforms()
    platform_info = next((p for p in available if p["id"] == platform), None)
    if not platform_info:
        return {"success": False, "message": "不支持的平台"}

    # 获取授权 URL
    oauth_platform = get_platform(platform)
    if not oauth_platform:
        return {"success": False, "message": "平台配置错误"}

    auth_url = oauth_platform.get_authorization_url()
    return {"success": True, "authorization_url": auth_url}


@router.post("/oauth/{platform}/callback")
async def oauth_callback(platform: str, code: str, request: Request):
    """处理 OAuth 回调"""
    from ..platforms.base import get_platform

    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    oauth_platform = get_platform(platform)
    if not oauth_platform:
        return {"success": False, "message": "平台配置错误"}

    # 换取令牌
    token_result = oauth_platform.exchange_code_for_token(code)
    if token_result.get("access_token"):
        # 保存平台账号
        account = create_platform_account(
            user_id=user["user_id"],
            platform=platform,
            account_name=token_result.get("user_info", {}).get("name", ""),
            account_id=token_result.get("user_info", {}).get("openid", ""),
            access_token=token_result["access_token"],
            refresh_token=token_result.get("refresh_token", "")
        )
        return {"success": True, "account": account}

    return {"success": False, "message": "授权失败", "error": token_result}


@router.get("/oauth/platforms")
async def get_oauth_platforms():
    """获取支持 OAuth 的平台列表"""
    from ..platforms.base import get_available_platforms
    platforms = get_available_platforms()
    return {"success": True, "platforms": platforms}


# ============================================
# 内容统计 API
# ============================================

@router.get("/analytics/summary")
async def get_analytics_summary_api(request: Request):
    """获取内容统计摘要"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    # 获取用户的所有内容进行统计
    contents = get_user_contents(user["user_id"], limit=1000)

    total_views = sum(c.get("views", 0) for c in contents)
    total_likes = sum(c.get("likes", 0) for c in contents)
    total_revenue = sum(c.get("revenue", 0) for c in contents)
    total_content = len(contents)

    published = len([c for c in contents if c.get("status") == "published"])
    drafts = len([c for c in contents if c.get("status") == "draft"])
    pending = len([c for c in contents if c.get("status") == "pending"])

    return {
        "success": True,
        "summary": {
            "total_content": total_content,
            "published": published,
            "drafts": drafts,
            "pending": pending,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_revenue": total_revenue
        }
    }


# ============================================
# AI 内容生成 API
# ============================================

class ContentGenerateRequest(BaseModel):
    topic: str
    platform: str = "wechat_public"
    style: str = "专业"
    keywords: list[str] = []
    length: str = "中等"


@router.post("/ai/generate")
async def generate_content_api(request: Request, gen_request: ContentGenerateRequest):
    """AI 生成内容"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    try:
        from ..agents.content_generator import ContentGeneratorAgent
        from ..core.memory import get_memory

        agent = ContentGeneratorAgent(get_memory())

        result = await agent.run({
            "topic": gen_request.topic,
            "platform": gen_request.platform,
            "style": gen_request.style,
            "keywords": gen_request.keywords,
            "length": gen_request.length,
        })

        if result.get("success"):
            content_data = result.get("content", {})
            # 创建内容记录
            content = create_content(
                user_id=user["user_id"],
                title=content_data.get("title", gen_request.topic),
                body=content_data.get("body", ""),
                summary=content_data.get("body", "")[:200] if content_data.get("body") else "",
                tags=content_data.get("tags", []),
                category=gen_request.platform,
                ai_generated=True,
                ai_prompt=gen_request.topic
            )

            # 如果有平台适配版本，更新内容
            if result.get("platform_versions"):
                from ..core.database import update_content
                update_content(content["id"], user["user_id"],
                             platform_versions=result.get("platform_versions"))

            return {
                "success": True,
                "content": content,
                "generated": {
                    "title": content_data.get("title"),
                    "body": content_data.get("body"),
                    "tags": content_data.get("tags", []),
                    "platform_versions": result.get("platform_versions", {})
                }
            }
        else:
            return {"success": False, "message": result.get("error", "生成失败")}
    except Exception as e:
        return {"success": False, "message": f"生成失败: {str(e)}"}


@router.post("/ai/adapt")
async def adapt_content_api(request: Request, content_id: int, target_platforms: list[str]):
    """AI 适配内容到多平台"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    try:
        from ..agents.content_generator import ContentGeneratorAgent, ContentAdaptor
        from ..core.memory import get_memory

        content = get_content_by_id(content_id, user["user_id"])
        if not content:
            return {"success": False, "message": "内容不存在"}

        agent = ContentGeneratorAgent(get_memory())
        adaptor = ContentAdaptor(agent)

        from ..core.models import Content as ContentModel
        content_model = ContentModel(
            id=content["id"],
            user_id=user["user_id"],
            title=content.get("title", ""),
            body=content.get("body", ""),
        )

        versions = await adaptor.adapt(content_model, target_platforms)

        # 更新内容的平台版本
        update_content(content_id, user["user_id"], platform_versions=versions)

        return {"success": True, "versions": versions}
    except Exception as e:
        return {"success": False, "message": f"适配失败: {str(e)}"}


@router.get("/ai/mmx-status")
async def mmx_status_api():
    """检查 mmx-cli 状态"""
    try:
        from ..mmx_client import get_mmx_client, is_mmx_available
        client = get_mmx_client()
        available = is_mmx_available()
        return {
            "success": True,
            "available": available,
            "path": client.mmx_path or "未找到"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ============================================
# RBAC 权限管理 API
# ============================================

@router.get("/rbac/roles")
async def get_roles_api(request: Request):
    """获取所有角色"""
    await require_admin(request)
    roles = get_all_roles()
    return {"success": True, "roles": roles}


@router.get("/rbac/permissions")
async def get_permissions_api(request: Request):
    """获取所有权限"""
    await require_admin(request)
    permissions = get_all_permissions()
    return {"success": True, "permissions": permissions}


@router.get("/rbac/user/roles")
async def get_user_roles_api(request: Request, user_id: int = None):
    """获取用户角色"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    # 如果指定了 user_id 且不是本人，需要 admin 权限
    if user_id and user_id != user["user_id"]:
        await require_admin(request)

    target_user_id = user_id or user["user_id"]
    roles = get_user_roles(target_user_id)
    return {"success": True, "roles": roles}


@router.post("/rbac/user/roles")
async def assign_role_api(request: Request, user_id: int, role: str):
    """为用户分配角色"""
    await require_admin(request)
    result = assign_role_to_user(user_id, role)
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, "message": result.get("message")}


@router.get("/rbac/user/permissions")
async def get_user_permissions_api(request: Request, user_id: int = None):
    """获取用户权限"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    # 如果指定了 user_id 且不是本人，需要 admin 权限
    if user_id and user_id != user["user_id"]:
        await require_admin(request)

    target_user_id = user_id or user["user_id"]
    permissions = get_user_permissions(target_user_id)
    return {"success": True, "permissions": permissions}


# ============================================
# 数据分析 API
# ============================================

@router.post("/analytics")
async def create_analytics_api(request: Request, data: dict):
    """录入分析数据"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    platform = data.get("platform")
    date = data.get("date")  # YYYY-MM-DD 格式
    if not platform or not date:
        return {"success": False, "message": "缺少 platform 或 date 字段"}

    result = upsert_analytics(
        user_id=user["user_id"],
        platform=platform,
        date=date,
        views=data.get("views", 0),
        likes=data.get("likes", 0),
        comments=data.get("comments", 0),
        shares=data.get("shares", 0),
        followers=data.get("followers", 0),
        revenue=data.get("revenue", 0)
    )
    return {"success": True, "result": result}


@router.get("/analytics")
async def get_analytics_api(request: Request, platform: str = None, days: int = 30):
    """获取分析数据"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    analytics = get_user_analytics(user["user_id"], platform, days)
    return {"success": True, "analytics": analytics}


@router.get("/analytics/summary")
async def get_analytics_summary_full_api(request: Request):
    """获取分析数据汇总"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    summary = get_analytics_summary(user["user_id"])
    return {"success": True, "summary": summary}


# ============================================
# 定时发布 API
# ============================================

@router.post("/scheduled-posts")
async def create_scheduled_post_api(request: Request, data: dict):
    """创建定时发布任务"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    content_id = data.get("content_id")
    platform = data.get("platform")
    scheduled_at = data.get("scheduled_at")  # ISO 格式时间

    if not all([content_id, platform, scheduled_at]):
        return {"success": False, "message": "缺少必要字段"}

    result = create_scheduled_post(content_id, platform, scheduled_at)
    return {"success": True, "scheduled_post": result}


@router.get("/scheduled-posts")
async def get_scheduled_posts_api(request: Request, status: str = None):
    """获取定时发布任务"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    posts = get_scheduled_posts(status)
    return {"success": True, "scheduled_posts": posts}


@router.delete("/scheduled-posts/{post_id}")
async def delete_scheduled_post_api(post_id: int, request: Request):
    """取消定时发布任务"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    result = cancel_scheduled_post(post_id)
    return {"success": result.get("deleted", False), "message": "取消成功" if result.get("deleted") else "取消失败"}