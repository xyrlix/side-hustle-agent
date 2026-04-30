"""
平台 OAuth 接入基类
"""

from abc import ABC, abstractmethod
from typing import Optional
import requests


class PlatformOAuth(ABC):
    """平台 OAuth 基类"""

    # 平台标识
    platform_id: str = ""
    platform_name: str = ""

    # OAuth 配置（子类需要覆盖）
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""

    # 令牌存储（由子类实现）
    _tokens: dict = {}

    def __init__(self, access_token: str = None, refresh_token: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token

    @abstractmethod
    def get_authorization_url(self) -> str:
        """获取授权 URL"""
        pass

    @abstractmethod
    def exchange_code_for_token(self, code: str) -> dict:
        """用授权码换取令牌"""
        pass

    @abstractmethod
    def refresh_access_token(self) -> dict:
        """刷新访问令牌"""
        pass

    @abstractmethod
    def get_user_info(self) -> dict:
        """获取用户信息"""
        pass

    def is_token_valid(self) -> bool:
        """检查令牌是否有效"""
        return bool(self.access_token)

    def api_request(self, method: str, url: str, **kwargs) -> dict:
        """发送 API 请求"""
        headers = kwargs.pop("headers", {})
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        response = requests.request(method, url, headers=headers, **kwargs)
        return response.json()


class WeChatPublicPlatform(PlatformOAuth):
    """微信公众号平台"""

    platform_id = "wechat_public"
    platform_name = "公众号"

    # 微信公众号 OAuth 配置
    # 需要在微信公众平台设置
    _authorize_url = "https://mp.weixin.qq.com/cgi-bin/componentloginpage"
    _api_base = "https://api.weixin.qq.com"

    def get_authorization_url(self) -> str:
        """获取授权 URL"""
        # 微信公众号使用第三方平台授权
        appid = self.client_id or os.getenv("WECHAT_APPID", "")
        redirect_uri = self.redirect_uri or os.getenv("WECHAT_REDIRECT_URI", "")
        return f"https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid={appid}&redirect_uri={redirect_uri}"

    def exchange_code_for_token(self, code: str) -> dict:
        """用授权码换取令牌"""
        # 微信公众号授权流程
        url = f"{self._api_base}/cgi-bin/component/api_query_auth"
        # 实现兑换逻辑
        return {"access_token": None, "refresh_token": None}

    def refresh_access_token(self) -> dict:
        """刷新访问令牌"""
        return {"access_token": None, "refresh_token": None}

    def get_user_info(self) -> dict:
        """获取用户信息"""
        url = f"{self._api_base}/cgi-bin/user/info"
        return self.api_request("GET", url, params={"access_token": self.access_token})

    def create_draft(self, title: str, content: str, thumb_media_id: str = None) -> dict:
        """创建草稿"""
        url = f"{self._api_base}/cgi-bin/draft/add"
        data = {
            "articles": [
                {
                    "title": title,
                    "content": content,
                    "thumb_media_id": thumb_media_id,
                    "author": "",
                    "digest": content[:54],
                    "show_cover_pic": 1,
                }
            ]
        }
        return self.api_request("POST", url, json=data)

    def publish_article(self, media_id: str) -> dict:
        """发布草稿"""
        url = f"{self._api_base}/cgi-bin/freepublish/submit"
        data = {"media_id": media_id}
        return self.api_request("POST", url, json=data)


class ToutiaoPlatform(PlatformOAuth):
    """头条号平台"""

    platform_id = "toutiao"
    platform_name = "头条号"

    # 头条号 OAuth 配置
    _authorize_url = "https://oauth.toutiao.com/authorize"
    _token_url = "https://oauth.toutiao.com/token"
    _api_base = "https://mp.toutiao.com"

    def get_authorization_url(self) -> str:
        """获取授权 URL"""
        client_id = self.client_id or os.getenv("TOUTIAO_CLIENT_ID", "")
        redirect_uri = self.redirect_uri or os.getenv("TOUTIAO_REDIRECT_URI", "")
        return f"{self._authorize_url}?client_key={client_id}&redirect_uri={redirect_uri}&response_type=code"

    def exchange_code_for_token(self, code: str) -> dict:
        """用授权码换取令牌"""
        import os
        url = self._token_url
        data = {
            "client_key": self.client_id or os.getenv("TOUTIAO_CLIENT_ID", ""),
            "client_secret": self.client_secret or os.getenv("TOUTIAO_CLIENT_SECRET", ""),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(url, data=data)
        result = response.json()
        if result.get("access_token"):
            self.access_token = result["access_token"]
            self.refresh_token = result.get("refresh_token")
        return result

    def refresh_access_token(self) -> dict:
        """刷新访问令牌"""
        import os
        url = self._token_url
        data = {
            "client_key": self.client_id or os.getenv("TOUTIAO_CLIENT_ID", ""),
            "client_secret": self.client_secret or os.getenv("TOUTIAO_CLIENT_SECRET", ""),
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        response = requests.post(url, data=data)
        result = response.json()
        if result.get("access_token"):
            self.access_token = result["access_token"]
            self.refresh_token = result.get("refresh_token")
        return result

    def get_user_info(self) -> dict:
        """获取用户信息"""
        url = f"{self._api_base}/api/v1/user/info/"
        return self.api_request("GET", url)

    def submit_article(self, title: str, content: str, tags: list = None) -> dict:
        """提交文章"""
        url = f"{self._api_base}/api/v1/article/submit/"
        data = {
            "title": title,
            "content": content,
            "content_type": "article",
            "labels": ",".join(tags) if tags else "",
        }
        return self.api_request("POST", url, json=data)


class XiaohongshuPlatform(PlatformOAuth):
    """小红书平台"""

    platform_id = "xiaohongshu"
    platform_name = "小红书"

    # 小红书 OAuth 配置
    # 注意：小红书的 API 需要申请才能使用
    _authorize_url = "https://edith.xiaohongshu.com/oauth_authorize"
    _api_base = "https://edith.xiaohongshu.com"

    def get_authorization_url(self) -> str:
        """获取授权 URL"""
        client_id = self.client_id or os.getenv("XHS_CLIENT_ID", "")
        redirect_uri = self.redirect_uri or os.getenv("XHS_REDIRECT_URI", "")
        return f"{self._authorize_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"

    def exchange_code_for_token(self, code: str) -> dict:
        """用授权码换取令牌"""
        url = f"{self._api_base}/api/v1/oauth/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(url, data=data)
        result = response.json()
        if result.get("access_token"):
            self.access_token = result["access_token"]
            self.refresh_token = result.get("refresh_token")
        return result

    def refresh_access_token(self) -> dict:
        """刷新访问令牌"""
        url = f"{self._api_base}/api/v1/oauth/refresh"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        response = requests.post(url, data=data)
        result = response.json()
        if result.get("access_token"):
            self.access_token = result["access_token"]
            self.refresh_token = result.get("refresh_token")
        return result

    def get_user_info(self) -> dict:
        """获取用户信息"""
        url = f"{self._api_base}/api/v1/user/info"
        return self.api_request("GET", url)

    def publish_note(self, title: str, content: str, images: list = None) -> dict:
        """发布笔记"""
        url = f"{self._api_base}/api/v1/note/publish"
        data = {
            "title": title,
            "desc": content,
            "image_list": images or [],
        }
        return self.api_request("POST", url, json=data)


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
        },
        {
            "id": "toutiao",
            "name": "头条号",
            "description": "今日头条平台，算法分发，适合资讯类内容",
            "oauth_required": True,
        },
        {
            "id": "xiaohongshu",
            "name": "小红书",
            "description": "种草社区，适合生活方式和美妆内容",
            "oauth_required": True,
        },
        {
            "id": "zhihu",
            "name": "知乎",
            "description": "专业问答社区，适合深度分析和专业内容",
            "oauth_required": False,
        },
    ]


# 兼容导入
import os
