"""
共享记忆池 —— 多 Agent 间的共享状态存储
"""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Any

from .models import ConversationContext, MemoryEntry


class SharedMemory:
    """
    共享记忆池

    三个 Agent 通过共享记忆池传递中间状态，实现协作推理。
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._memory: dict[str, Any] = {}
        self._history: list[MemoryEntry] = []
        self._context = ConversationContext()

    def set(self, key: str, value: Any, agent: str = "system") -> None:
        """设置记忆"""
        with self._lock:
            self._memory[key] = value
            self._history.append(MemoryEntry(
                agent=agent,
                key=key,
                value=value,
                timestamp=datetime.now()
            ))

    def get(self, key: str, default: Any = None) -> Any:
        """获取记忆"""
        with self._lock:
            return self._memory.get(key, default)

    def get_context(self) -> ConversationContext:
        """获取当前对话上下文"""
        with self._lock:
            return self._context.model_copy(deep=True)

    def update_context(self, **kwargs) -> None:
        """更新对话上下文"""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._context, key):
                    setattr(self._context, key, value)

    def get_history(self, agent: str | None = None) -> list[MemoryEntry]:
        """获取记忆历史"""
        with self._lock:
            if agent:
                return [e for e in self._history if e.agent == agent]
            return list(self._history)

    def clear(self) -> None:
        """清空记忆"""
        with self._lock:
            self._memory.clear()
            self._history.clear()
            self._context = ConversationContext()

    def reset_context(self) -> None:
        """重置对话上下文"""
        with self._lock:
            self._context = ConversationContext()


# 全局共享记忆实例
_memory_instance: SharedMemory | None = None


def get_memory() -> SharedMemory:
    """获取共享记忆单例"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = SharedMemory()
    return _memory_instance
