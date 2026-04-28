"""
LLM Provider 抽象层

支持多种大模型：OpenAI、DeepSeek、MiniMax、千问(Kimim)、Anthropic 等
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import httpx


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model: str
    usage: dict | None = None
    finish_reason: str | None = None


class BaseLLMProvider(ABC):
    """LLM Provider 基类"""

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.extra_params = kwargs

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        """发送对话请求"""
        pass

    def _build_messages(self, prompt: str, system_prompt: str | None = None) -> list[dict]:
        """构建消息格式"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages


class OpenAIProvider(BaseLLMProvider):
    """OpenAI / Azure OpenAI / 兼容 API"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: str | None = None,
        **kwargs
    ):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://api.openai.com/v1"

    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        url = f"{self.base_url.rstrip('/')}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            **self.extra_params,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", self.model),
                usage=data.get("usage"),
                finish_reason=data["choices"][0].get("finish_reason"),
            )


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek 大模型"""

    def __init__(self, api_key: str, model: str = "deepseek-chat", **kwargs):
        super().__init__(api_key, model, **kwargs)

    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        url = "https://api.deepseek.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            **self.extra_params,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", self.model),
                usage=data.get("usage"),
                finish_reason=data["choices"][0].get("finish_reason"),
            )


class MiniMaxProvider(BaseLLMProvider):
    """MiniMax 大模型"""

    def __init__(self, api_key: str, model: str = "MiniMax-Text-01", group_id: str | None = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.group_id = group_id

    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "group_id": self.group_id,
            **self.extra_params,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", self.model),
                usage=data.get("usage"),
                finish_reason=data["choices"][0].get("finish_reason"),
            )


class QwenProvider(BaseLLMProvider):
    """阿里云千问 (Qwen) 大模型"""

    def __init__(
        self,
        api_key: str,
        model: str = "qwen-turbo",
        api_version: str = "2024-08-01",
        **kwargs
    ):
        super().__init__(api_key, model, **kwargs)
        self.api_version = api_version

    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        url = f"https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            **self.extra_params,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", self.model),
                usage=data.get("usage"),
                finish_reason=data["choices"][0].get("finish_reason"),
            )


class KimiProvider(BaseLLMProvider):
    """Kimi (Moonshot) 大模型"""

    def __init__(self, api_key: str, model: str = "moonshot-v1-8k", **kwargs):
        super().__init__(api_key, model, **kwargs)

    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        url = "https://api.moonshot.cn/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            **self.extra_params,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", self.model),
                usage=data.get("usage"),
                finish_reason=data["choices"][0].get("finish_reason"),
            )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude 模型"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", **kwargs):
        super().__init__(api_key, model, **kwargs)

    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        url = "https://api.anthropic.com/v1/messages"

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        # 转换消息格式
        system = None
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
                break

        user_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages if msg["role"] != "system"
        ]

        payload = {
            "model": self.model,
            "messages": user_messages,
            "max_tokens": kwargs.pop("max_tokens", 2048),
            **self.extra_params,
            **kwargs,
        }

        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["content"][0]["text"],
                model=data.get("model", self.model),
                usage=data.get("usage"),
                finish_reason=data.get("stop_reason"),
            )


# Provider 工厂
LLM_PROVIDERS = {
    "openai": OpenAIProvider,
    "deepseek": DeepSeekProvider,
    "minimax": MiniMaxProvider,
    "qwen": QwenProvider,
    "kimi": KimiProvider,
    "anthropic": AnthropicProvider,
}


def create_llm_provider(
    provider: str,
    api_key: str,
    model: str | None = None,
    **kwargs
) -> BaseLLMProvider:
    """创建 LLM Provider"""
    provider_cls = LLM_PROVIDERS.get(provider.lower())
    if not provider_cls:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(LLM_PROVIDERS.keys())}")

    # 默认模型
    defaults = {
        "openai": "gpt-4o",
        "deepseek": "deepseek-chat",
        "minimax": "MiniMax-Text-01",
        "qwen": "qwen-turbo",
        "kimi": "moonshot-v1-8k",
        "anthropic": "claude-sonnet-4-20250514",
    }

    if model is None:
        model = defaults.get(provider.lower(), "gpt-4o")

    return provider_cls(api_key=api_key, model=model, **kwargs)