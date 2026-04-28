"""
配置管理

支持的环境变量:
- LLM_PROVIDER: deepseek/minimax/qwen/kimi/openai/anthropic (默认: deepseek)
- LLM_API_KEY: API Key
- LLM_MODEL: 模型名称 (可选，有默认值)
- 其他 Provider 特定变量: DEEPSEEK_API_KEY, QWEN_API_KEY 等
"""

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # LLM Provider 配置
    llm_provider: str = Field(default="deepseek", description="LLM 提供商: deepseek/minimax/qwen/kimi/openai/anthropic")
    llm_api_key: str = Field(default="", description="LLM API Key")
    llm_model: str = Field(default="", description="LLM 模型名称")

    # 兼容旧配置 (deprecated)
    anthropic_api_key: str = Field(default="", description="[Deprecated] 使用 LLM_API_KEY")
    anthropic_model: str = Field(default="", description="[Deprecated] 使用 LLM_MODEL")

    # MiniMax 特定配置
    minimax_group_id: str = Field(default="", description="MiniMax Group ID")

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
        env_prefix = ""
        case_sensitive = False
        extra = "allow"  # 允许额外字段

    def get_llm_config(self) -> dict:
        """获取 LLM 配置"""
        # 优先使用新配置
        if self.llm_api_key:
            api_key = self.llm_api_key
        elif self.anthropic_api_key:  # 兼容旧配置
            api_key = self.anthropic_api_key
        else:
            # 尝试从环境变量读取
            provider = self.llm_provider
            if provider == "deepseek":
                api_key = os.getenv("DEEPSEEK_API_KEY", "")
            elif provider == "qwen":
                api_key = os.getenv("QWEN_API_KEY", "")
            elif provider == "kimi":
                api_key = os.getenv("KIMI_API_KEY", "")
            elif provider == "minimax":
                api_key = os.getenv("MINIMAX_API_KEY", "")
            elif provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY", "")
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY", "")
            else:
                api_key = ""

        model = self.llm_model
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

        config = {
            "provider": self.llm_provider,
            "api_key": api_key,
            "model": model,
        }

        # Provider 特定配置
        if self.llm_provider == "minimax" and self.minimax_group_id:
            config["group_id"] = self.minimax_group_id

        return config


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()