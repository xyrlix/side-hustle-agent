"""
Agent 基类
"""

from abc import ABC, abstractmethod
from typing import Any

import anthropic
from anthropic import Anthropic

from ..core.config import get_settings
from ..core.memory import SharedMemory, get_memory
from ..core.models import AgentState


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, name: str, memory: SharedMemory | None = None):
        self.name = name
        self.memory = memory or get_memory()
        self.settings = get_settings()
        self.state = AgentState.IDLE

        self._client: Anthropic | None = None

    @property
    def client(self) -> Anthropic:
        """获取 Anthropic 客户端"""
        if self._client is None:
            api_key = self.settings.anthropic_api_key
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY is not set")
            self._client = Anthropic(api_key=api_key)
        return self._client

    def update_state(self, state: AgentState) -> None:
        """更新状态"""
        self.state = state
        self.memory.update_context(agent_state=state)

    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        """运行 Agent"""
        pass

    def think(self, prompt: str, system_prompt: str | None = None) -> str:
        """调用 LLM 进行推理"""
        messages = [{"role": "user", "content": prompt}]

        system_parts = []
        if system_prompt:
            system_parts.append(system_prompt)

        response = self.client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=2048,
            temperature=self.settings.temperature,
            system="\n".join(system_parts) if system_parts else None,
            messages=messages,
        )

        return response.content[0].text

    async def think_async(self, prompt: str, system_prompt: str | None = None) -> str:
        """异步调用 LLM"""
        import asyncio

        def _call():
            return self.think(prompt, system_prompt)

        return await asyncio.to_thread(_call)
