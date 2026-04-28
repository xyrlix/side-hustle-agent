"""
API 路由
"""

from typing import Any

from fastapi import APIRouter

from ..core.models import UserInput
from ..orchestrator import SideHustleOrchestrator

router = APIRouter(prefix="/api", tags=["副业推荐"])


@router.post("/recommend")
async def recommend_side_hustle(user_input: UserInput) -> dict[str, Any]:
    """
    获取副业推荐

    请求体：
    ```json
    {
        "city": "上海",
        "skills": ["Python", "Excel"],
        "available_time": "每天1-2小时",
        "risk_preference": "稳健型",
        "avoid_appearing": true,
        "monthly_goal": 5000
    }
    ```
    """
    orchestrator = SideHustleOrchestrator()
    result = await orchestrator.run(user_input)
    return result


@router.post("/feedback")
async def submit_feedback(
    user_input: UserInput,
    feedback: str,
    reason: str | None = None
) -> dict[str, Any]:
    """
    提交执行反馈

    用于迭代优化推荐结果：
    - success: 执行成功
    - failed: 执行失败（可提供原因）
    - adjust: 需要调整
    """
    orchestrator = SideHustleOrchestrator()
    result = await orchestrator.run_with_feedback(user_input, feedback)
    return result
