"""
平台 OAuth 接入模块

支持微信公众号、头条号、小红书等平台的 OAuth 接入和内容发布。
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
import os
import logging
import time
import httpx
from dataclasses import dataclass, field

logger = logging.getLogger("side_hustle_agent.platforms")


@dataclass
class PlatformConfig:
    """平台配置"""
    platform_id: str
    platform_name: str
    client_id_env: str  # 环境变量名
    client_secret_env: str
    redirect_uri_env: str
    authorize_url: str
    token_url: str
    api_base: str


@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    platform: str
    published_url: str = ""
    platform_content_id: str = ""
    error: str = ""
    data: dict = field(default_factory=dict)


class PlatformOAuth(ABC):
    """平台 OAuth 基类"""

    # 平台配置（子类覆盖）
    config: PlatformConfig = None

    # 实例配置
    _client_id: str = ""
    _client_secret: str = ""
    _redirect_uri: str = ""

    # 令牌
    _access_token: str = ""
    _refresh_token: str = ""
    _token_expires_at: float = 0

    def __init__(self, access_token: str = None, refresh_token: str = None):
        self._access_token = access_token or ""
        self._refresh_token = refresh_token or ""

    @property
    def client_id(self) -> str:
        if self._client_id:
            return self._client_id
        if self.config:
            return os.getenv(self.config.client_id_env, "")
        return ""

    @property
    def client_secret(self) -> str:
        if self._client_secret:
            return self._client_secret
        if self.config:
            return os.getenv(self.config.client_secret_env, "")
        return ""

    @property
    def redirect_uri(self) -> str:
        if self._redirect_uri:
            return self._redirect_uri
        if self.config:
            return os.getenv(self.config.redirect_uri_env, "")
        return os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/api/oauth/callback")

    @abstractmethod
    def get_authorization_url(self) -> str:
        """获取授权 URL"""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> dict:
        """用授权码换取令牌"""
        pass

    @abstractmethod
    async def refresh_access_token(self) -> dict:
        """刷新访问令牌"""
        pass

    @abstractmethod
    async def get_user_info(self) -> dict:
        """获取用户信息"""
        pass

    def is_token_valid(self) -> bool:
        """检查令牌是否有效"""
        if not self._access_token:
            return False
        # 提前5分钟判断是否需要刷新
        if self._token_expires_at > 0 and time.time() > self._token_expires_at - 300:
            return False
        return True

    async def api_request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        params: dict = None,
        headers: dict = None,
    ) -> dict:
        """发送 API 请求（异步）"""
        url = f"{self.config.api_base}{endpoint}" if self.config else endpoint

        req_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._access_token:
            req_headers["Authorization"] = f"Bearer {self._access_token}"
        if headers:
            req_headers.update(headers)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=req_headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=req_headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=req_headers, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=req_headers, params=params)
                else:
                    return {"success": False, "error": f"Unsupported method: {method}"}

                if response.status_code >= 400:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text[:200]}",
                        "status_code": response.status_code,
                    }

                try:
                    result = response.json()
                    return result
                except Exception:
                    return {"success": False, "error": "Invalid JSON response", "text": response.text[:200]}

        except httpx.TimeoutException:
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def ensure_valid_token(self) -> bool:
        """确保令牌有效，必要时刷新"""
        if self.is_token_valid():
            return True

        if self._refresh_token:
            result = await self.refresh_access_token()
            return result.get("success", False)

        return False


class WeChatPublicPlatform(PlatformOAuth):
    """微信公众号平台"""

    config = PlatformConfig(
        platform_id="wechat_public",
        platform_name="公众号",
        client_id_env="WECHAT_APPID",
        client_secret_env="WECHAT_APPSECRET",
        redirect_uri_env="WECHAT_REDIRECT_URI",
        authorize_url="https://mp.weixin.qq.com/cgi-bin/componentloginpage",
        token_url="https://api.weixin.qq.com/cgi-bin/component/api_component_token",
        api_base="https://api.weixin.qq.com",
    )

    async def get_authorization_url(self) -> str:
        """获取授权 URL"""
        appid = self.client_id
        redirect_uri = self.redirect_uri
        return f"https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid={appid}&redirect_uri={redirect_uri}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """用授权码换取令牌"""
        # 微信公众号使用第三方平台授权流程
        result = await self.api_request(
            "POST",
            "/cgi-bin/component/api_component_token",
            data={
                "component_appid": self.client_id,
                "component_appsecret": self.client_secret,
                "authorization_code": code,
            }
        )

        if result.get("component_access_token"):
            self._access_token = result["component_access_token"]
            self._token_expires_at = time.time() + result.get("expires_in", 7200)
            return {
                "success": True,
                "access_token": result["component_access_token"],
                "expires_in": result.get("expires_in", 7200),
            }

        return {"success": False, "error": result.get("errmsg", "Unknown error")}

    async def refresh_access_token(self) -> dict:
        """刷新访问令牌"""
        # 微信公众号不支持refresh_token，需要重新授权
        return {"success": False, "error": "微信公众号不支持令牌刷新，请重新授权"}

    async def get_user_info(self) -> dict:
        """获取用户信息"""
        if not await self.ensure_valid_token():
            return {"success": False, "error": "Token invalid"}

        result = await self.api_request(
            "GET",
            "/cgi-bin/user/info",
            params={"access_token": self._access_token, "openid": "OPENID", "lang": "zh_CN"}
        )
        return result

    async def create_draft(self, title: str, content: str, thumb_media_id: str = None) -> dict:
        """创建草稿"""
        if not await self.ensure_valid_token():
            return {"success": False, "error": "Token invalid"}

        article = {
            "title": title,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "author": "",
            "digest": content[:54] if content else "",
            "show_cover_pic": 1,
        }

        result = await self.api_request(
            "POST",
            "/cgi-bin/draft/add",
            data={"articles": [article]},
            headers={"Access-Token": self._access_token}
        )

        if result.get("media_id"):
            return {"success": True, "media_id": result["media_id"]}
        return {"success": False, "error": result.get("errmsg", "Failed to create draft")}

    async def publish_article(self, media_id: str) -> dict:
        """发布草稿"""
        if not await self.ensure_valid_token():
            return {"success": False, "error": "Token invalid"}

        result = await self.api_request(
            "POST",
            "/cgi-bin/freepublish/submit",
            data={"media_id": media_id},
            headers={"Access-Token": self._access_token}
        )

        if result.get("msgid"):
            return {
                "success": True,
                "msg_id": result["msgid"],
                "url": f"https://mp.weixin.qq.com/s/{media_id}"
            }
        return {"success": False, "error": result.get("errmsg", "Failed to publish")}

    async def publish(self, title: str, content: str, thumb_media_id: str = None) -> PublishResult:
        """一键发布到公众号"""
        try:
            # 1. 创建草稿
            draft_result = await self.create_draft(title, content, thumb_media_id)
            if not draft_result.get("success"):
                return PublishResult(
                    success=False,
                    platform="wechat_public",
                    error=f"创建草稿失败: {draft_result.get('error')}"
                )

            media_id = draft_result.get("media_id")

            # 2. 发布草稿
            publish_result = await self.publish_article(media_id)
            if not publish_result.get("success"):
                return PublishResult(
                    success=False,
                    platform="wechat_public",
                    error=f"发布失败: {publish_result.get('error')}"
                )

            return PublishResult(
                success=True,
                platform="wechat_public",
                published_url=publish_result.get("url", ""),
                platform_content_id=media_id,
                data=publish_result
            )

        except Exception as e:
            logger.error(f"WeChat publish failed: {str(e)}")
            return PublishResult(
                success=False,
                platform="wechat_public",
                error=str(e)
            )


class ToutiaoPlatform(PlatformOAuth):
    """头条号平台"""

    config = PlatformConfig(
        platform_id="toutiao",
        platform_name="头条号",
        client_id_env="TOUTIAO_CLIENT_ID",
        client_secret_env="TOUTIAO_CLIENT_SECRET",
        redirect_uri_env="TOUTIAO_REDIRECT_URI",
        authorize_url="https://oauth.toutiao.com/authorize",
        token_url="https://oauth.toutiao.com/token",
        api_base="https://mp.toutiao.com",
    )

    async def get_authorization_url(self) -> str:
        """获取授权 URL"""
        client_id = self.client_id
        redirect_uri = self.redirect_uri
        state = os.urandom(16).hex()
        return f"{self.config.authorize_url}?client_key={client_id}&redirect_uri={redirect_uri}&response_type=code&state={state}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """用授权码换取令牌"""
        result = await self.api_request(
            "POST",
            self.config.token_url,
            data={
                "client_key": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
        )

        if result.get("data", {}).get("access_token"):
            data = result["data"]
            self._access_token = data["access_token"]
            self._refresh_token = data.get("refresh_token", "")
            self._token_expires_at = time.time() + data.get("expires_in", 7200)
            return {
                "success": True,
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token"),
                "expires_in": data.get("expires_in", 7200),
            }

        return {"success": False, "error": result.get("message", "Unknown error")}

    async def refresh_access_token(self) -> dict:
        """刷新访问令牌"""
        if not self._refresh_token:
            return {"success": False, "error": "No refresh token"}

        result = await self.api_request(
            "POST",
            self.config.token_url,
            data={
                "client_key": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            }
        )

        if result.get("data", {}).get("access_token"):
            data = result["data"]
            self._access_token = data["access_token"]
            self._refresh_token = data.get("refresh_token", "")
            self._token_expires_at = time.time() + data.get("expires_in", 7200)
            return {"success": True, "access_token": data["access_token"]}

        return {"success": False, "error": result.get("message", "Failed to refresh")}

    async def get_user_info(self) -> dict:
        """获取用户信息"""
        if not await self.ensure_valid_token():
            return {"success": False, "error": "Token invalid"}

        result = await self.api_request(
            "GET",
            "/api/v1/user/info/",
            params={"access_token": self._access_token}
        )
        return result

    async def submit_article(self, title: str, content: str, tags: list = None, cover_images: list = None) -> dict:
        """提交文章"""
        if not await self.ensure_valid_token():
            return {"success": False, "error": "Token invalid"}

        data = {
            "title": title,
            "content": content,
            "content_type": "article",
            "labels": ",".join(tags) if tags else "",
            "cover_images": cover_images or [],
        }

        result = await self.api_request(
            "POST",
            "/api/v1/article/submit/",
            data=data,
            headers={"Access-Token": self._access_token}
        )

        return result

    async def publish(self, title: str, content: str, tags: list = None) -> PublishResult:
        """一键发布到头条号"""
        try:
            result = await self.submit_article(title, content, tags)

            if result.get("data", {}).get("article_id"):
                article_id = result["data"]["article_id"]
                return PublishResult(
                    success=True,
                    platform="toutiao",
                    published_url=f"https://www.toutiao.com/a/{article_id}",
                    platform_content_id=str(article_id),
                    data=result
                )

            return PublishResult(
                success=False,
                platform="toutiao",
                error=result.get("message", result.get("error", "Unknown error"))
            )

        except Exception as e:
            logger.error(f"Toutiao publish failed: {str(e)}")
            return PublishResult(
                success=False,
                platform="toutiao",
                error=str(e)
            )


class XiaohongshuPlatform(PlatformOAuth):
    """小红书平台"""

    config = PlatformConfig(
        platform_id="xiaohongshu",
        platform_name="小红书",
        client_id_env="XHS_CLIENT_ID",
        client_secret_env="XHS_CLIENT_SECRET",
        redirect_uri_env="XHS_REDIRECT_URI",
        authorize_url="https://edith.xiaohongshu.com/oauth_authorize",
        token_url="https://edith.xiaohongshu.com/api/v1/oauth/token",
        api_base="https://edith.xiaohongshu.com",
    )

    async def get_authorization_url(self) -> str:
        """获取授权 URL"""
        client_id = self.client_id
        redirect_uri = self.redirect_uri
        state = os.urandom(16).hex()
        return f"{self.config.authorize_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state={state}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """用授权码换取令牌"""
        result = await self.api_request(
            "POST",
            self.config.token_url,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
        )

        if result.get("data", {}).get("access_token"):
            data = result["data"]
            self._access_token = data["access_token"]
            self._refresh_token = data.get("refresh_token", "")
            self._token_expires_at = time.time() + data.get("expires_in", 7200)
            return {
                "success": True,
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token"),
            }

        return {"success": False, "error": result.get("error", "Unknown error")}

    async def refresh_access_token(self) -> dict:
        """刷新访问令牌"""
        if not self._refresh_token:
            return {"success": False, "error": "No refresh token"}

        result = await self.api_request(
            "POST",
            "/api/v1/oauth/refresh",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            }
        )

        if result.get("data", {}).get("access_token"):
            data = result["data"]
            self._access_token = data["access_token"]
            self._refresh_token = data.get("refresh_token", "")
            self._token_expires_at = time.time() + data.get("expires_in", 7200)
            return {"success": True}

        return {"success": False, "error": result.get("error", "Failed to refresh")}

    async def get_user_info(self) -> dict:
        """获取用户信息"""
        if not await self.ensure_valid_token():
            return {"success": False, "error": "Token invalid"}

        result = await self.api_request(
            "GET",
            "/api/v1/user/info",
            headers={"X-s": self._access_token}
        )
        return result

    async def publish_note(self, title: str, content: str, images: list = None, tags: list = None) -> dict:
        """发布笔记"""
        if not await self.ensure_valid_token():
            return {"success": False, "error": "Token invalid"}

        data = {
            "title": title,
            "desc": content,
            "image_list": images or [],
            "tags": tags or [],
        }

        result = await self.api_request(
            "POST",
            "/api/v1/note/publish",
            data=data,
            headers={"X-s": self._access_token}
        )

        return result

    async def publish(self, title: str, content: str, images: list = None, tags: list = None) -> PublishResult:
        """一键发布到小红书"""
        try:
            result = await self.publish_note(title, content, images, tags)

            if result.get("data", {}).get("note_id"):
                note_id = result["data"]["note_id"]
                return PublishResult(
                    success=True,
                    platform="xiaohongshu",
                    published_url=f"https://www.xiaohongshu.com/explore/{note_id}",
                    platform_content_id=note_id,
                    data=result
                )

            return PublishResult(
                success=False,
                platform="xiaohongshu",
                error=result.get("error", "Unknown error")
            )

        except Exception as e:
            logger.error(f"Xiaohongshu publish failed: {str(e)}")
            return PublishResult(
                success=False,
                platform="xiaohongshu",
                error=str(e)
            )


# 平台注册表
PLATFORMS = {
    "wechat_public": WeChatPublicPlatform,
    "toutiao": ToutiaoPlatform,
    "xiaohongshu": XiaohongshuPlatform,
}


def get_platform(platform_id: str, **kwargs) -> Optional[PlatformOAuth]:
    """获取平台实例"""
    platform_class = PLATFORMS.get(platform_id)
    if not platform_class:
        return None
    return platform_class(**kwargs)


def get_available_platforms() -> list:
    """获取可用的平台列表"""
    return [
        {
            "id": "wechat_public",
            "name": "公众号",
            "description": "微信公众平台，适合深度文章和知识付费",
            "oauth_required": True,
            "features": ["文章", "草稿箱", "自动发布"],
        },
        {
            "id": "toutiao",
            "name": "头条号",
            "description": "今日头条平台，算法分发，适合资讯类内容",
            "oauth_required": True,
            "features": ["文章", "视频", "头条小店"],
        },
        {
            "id": "xiaohongshu",
            "name": "小红书",
            "description": "种草社区，适合生活方式和美妆内容",
            "oauth_required": True,
            "features": ["图文笔记", "视频笔记", "好物推荐"],
        },
        {
            "id": "zhihu",
            "name": "知乎",
            "description": "专业问答社区，适合深度分析和专业内容",
            "oauth_required": False,
            "features": ["文章", "回答", "专栏"],
        },
    ]


async def publish_to_platform(
    platform_id: str,
    title: str,
    content: str,
    access_token: str = None,
    refresh_token: str = None,
    **kwargs
) -> PublishResult:
    """通用的平台发布函数"""
    platform = get_platform(platform_id, access_token=access_token, refresh_token=refresh_token)
    if not platform:
        return PublishResult(
            success=False,
            platform=platform_id,
            error=f"Unknown platform: {platform_id}"
        )

    try:
        if platform_id == "wechat_public":
            return await platform.publish(title, content, kwargs.get("thumb_media_id"))
        elif platform_id == "toutiao":
            return await platform.publish(title, content, kwargs.get("tags"))
        elif platform_id == "xiaohongshu":
            return await platform.publish(
                title, content,
                images=kwargs.get("images"),
                tags=kwargs.get("tags")
            )
        else:
            return PublishResult(
                success=False,
                platform=platform_id,
                error=f"Platform {platform_id} does not support auto-publish yet"
            )
    except Exception as e:
        logger.error(f"publish_to_platform failed: {str(e)}")
        return PublishResult(
            success=False,
            platform=platform_id,
            error=str(e)
        )


# 兼容导入
import os