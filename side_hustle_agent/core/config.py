"""
配置管理
"""

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # Anthropic API
    anthropic_api_key: str = Field(default="", description="Anthropic API Key")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514", description="使用的模型")

    # 应用配置
    app_name: str = "副业雷达"
    debug: bool = Field(default=False, description="调试模式")

    # Agent 配置
    max_retries: int = Field(default=3, description="最大重试次数")
    temperature: float = Field(default=0.7, ge=0, le=1, description="LLM 温度参数")

    # 知识库路径
    knowledge_base_path: str = Field(default="side_hustle_agent/knowledge/side_hustles.json", description="知识库路径")

    # 地域数据
    city_tier_data: dict[str, str] = Field(default_factory=lambda: {
        "北京": "一线城市",
        "上海": "一线城市",
        "广州": "一线城市",
        "深圳": "一线城市",
        "成都": "二线城市",
        "杭州": "二线城市",
        "武汉": "二线城市",
        "西安": "二线城市",
    }, description="城市等级数据")

    class Config:
        env_prefix = "SIDE_HUSTLE_"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
