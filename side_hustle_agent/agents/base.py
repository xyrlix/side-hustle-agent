"""
Agent 基类

使用统一的 LLM Provider 接口，支持多种大模型。
"""

from abc import ABC, abstractmethod
from typing import Any

from ..core.config import get_settings
from ..core.memory import SharedMemory, get_memory
from ..core.models import AgentState
from ..llm import create_llm_provider, BaseLLMProvider


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, name: str, memory: SharedMemory | None = None):
        self.name = name
        self.memory = memory or get_memory()
        self.settings = get_settings()
        self.state = AgentState.IDLE

        self._llm: BaseLLMProvider | None = None

    @property
    def llm(self) -> BaseLLMProvider:
        """获取 LLM Provider"""
        if self._llm is None:
            llm_config = self.settings.get_llm_config()
            api_key = llm_config.get("api_key", "")

            if not api_key:
                raise ValueError(
                    f"LLM API Key not set. "
                    f"Set {llm_config['provider'].upper()}_API_KEY environment variable "
                    f"or configure llm_api_key in settings."
                )

            self._llm = create_llm_provider(
                provider=llm_config["provider"],
                api_key=api_key,
                model=llm_config.get("model"),
                **{k: v for k, v in llm_config.items() if k not in ["provider", "api_key", "model"]}
            )

        return self._llm

    def update_state(self, state: AgentState) -> None:
        """更新状态"""
        self.state = state
        self.memory.update_context(agent_state=state)

    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        """运行 Agent"""
        pass

    async def think(self, prompt: str, system_prompt: str | None = None) -> str:
        """调用 LLM 进行推理"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.llm.chat(
            messages=messages,
            temperature=self.settings.temperature,
            max_tokens=2048,
        )

        return response.content

    def think_sync(self, prompt: str, system_prompt: str | None = None) -> str:
        """同步调用 LLM"""
        import asyncio
        return asyncio.run(self.think(prompt, system_prompt))