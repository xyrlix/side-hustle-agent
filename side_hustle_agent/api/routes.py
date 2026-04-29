"""
API 路由
"""

from typing import Any

from fastapi import APIRouter

from ..core.models import UserInput
from ..core.config import update_runtime_config, get_runtime_config
from ..orchestrator import SideHustleOrchestrator

router = APIRouter(prefix="/api", tags=["副业推荐"])


@router.post("/recommend")
async def recommend_side_hustle(user_input: UserInput) -> dict[str, Any]:
    """获取副业推荐"""
    orchestrator = SideHustleOrchestrator()
    result = await orchestrator.run(user_input)
    return result


@router.post("/feedback")
async def submit_feedback(
    user_input: UserInput,
    feedback: str,
    reason: str | None = None
) -> dict[str, Any]:
    """提交执行反馈"""
    orchestrator = SideHustleOrchestrator()
    result = await orchestrator.run_with_feedback(user_input, feedback)
    return result


@router.get("/config")
async def get_config() -> dict[str, Any]:
    """获取当前 LLM 配置（不返回实际 API Key）"""
    config = get_runtime_config()
    return {
        "llm_provider": config.get("provider", "deepseek"),
        "llm_api_key": "********",
        "llm_model": config.get("model", "deepseek-chat"),
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