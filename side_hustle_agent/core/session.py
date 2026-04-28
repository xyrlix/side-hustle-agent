"""
会话管理
"""

import uuid
from datetime import datetime, timedelta
from typing import TypedDict

from ..core.models import ConversationContext


class Session(TypedDict):
    """会话数据"""
    session_id: str
    user_id: str | None
    created_at: datetime
    updated_at: datetime
    context: ConversationContext
    interaction_count: int


class SessionManager:
    """
    会话管理器

    管理用户会话，支持：
    - 会话创建和销毁
    - 会话状态追踪
    - 历史会话查询
    """

    def __init__(self, expire_minutes: int = 60):
        self._sessions: dict[str, Session] = {}
        self._expire_minutes = expire_minutes

    def create_session(self, user_id: str | None = None) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        session: Session = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "context": ConversationContext(),
            "interaction_count": 0,
        }
        self._sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str) -> Session | None:
        """获取会话"""
        session = self._sessions.get(session_id)

        if session and self._is_expired(session):
            self.delete_session(session_id)
            return None

        return session

    def update_session(self, session_id: str, **kwargs) -> bool:
        """更新会话"""
        session = self.get_session(session_id)
        if not session:
            return False

        session["updated_at"] = datetime.now()
        session["interaction_count"] += 1

        for key, value in kwargs.items():
            if key in session:
                if key == "context" and hasattr(value, "model_dump"):
                    session[key] = value
                else:
                    session[key] = value

        return True

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def _is_expired(self, session: Session) -> bool:
        """检查会话是否过期"""
        expire_time = session["updated_at"] + timedelta(minutes=self._expire_minutes)
        return datetime.now() > expire_time

    def cleanup_expired(self) -> int:
        """清理过期会话"""
        expired_ids = [
            sid for sid, session in self._sessions.items()
            if self._is_expired(session)
        ]
        for sid in expired_ids:
            self.delete_session(sid)
        return len(expired_ids)

    def get_user_sessions(self, user_id: str) -> list[Session]:
        """获取用户的所有会话"""
        return [
            s for s in self._sessions.values()
            if s["user_id"] == user_id
        ]


# 全局会话管理器
_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """获取会话管理器单例"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager