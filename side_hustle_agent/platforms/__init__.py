"""
平台 OAuth 接入模块
"""

from .base import (
    PlatformOAuth,
    WeChatPublicPlatform,
    ToutiaoPlatform,
    XiaohongshuPlatform,
    PLATFORMS,
    get_platform,
    get_available_platforms,
)

__all__ = [
    "PlatformOAuth",
    "WeChatPublicPlatform",
    "ToutiaoPlatform",
    "XiaohongshuPlatform",
    "PLATFORMS",
    "get_platform",
    "get_available_platforms",
]
