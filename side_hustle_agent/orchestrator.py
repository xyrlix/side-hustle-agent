"""
副业雷达多智能体系统

三层多 Agent 协同推理框架：
1. 用户理解 Agent (UserProfiler) - 解析用户画像
2. 副业知识图谱 Agent (OpportunityMiner) - 匹配副业
3. 执行规划 Agent (ActionPlanner) - 生成行动计划
4. 验证 Agent (Validator) - 事实核查
"""

from dataclasses import dataclass
from typing import Literal

from .agents import (
    ActionPlannerAgent,
    OpportunityMinerAgent,
    UserProfilerAgent,
    ValidatorAgent,
)
from .core.memory import SharedMemory, get_memory
from .core.models import (
    ActionPlan,
    ConversationContext,
    Recommendation,
    UserInput,
    UserProfile,
    ValidationResult,
)


@dataclass
class AgentResult:
    """Agent 执行结果"""
    success: bool
    message: str
    data: dict | None = None


class SideHustleOrchestrator:
    """
    副业雷达多智能体编排器

    协调三个 Agent 完成从用户画像到可执行方案的端到端生成。
    """

    def __init__(self, memory: SharedMemory | None = None):
        self.memory = memory or get_memory()

        # 初始化各 Agent
        self.user_profiler = UserProfilerAgent(self.memory)
        self.opportunity_miner = OpportunityMinerAgent(self.memory)
        self.action_planner = ActionPlannerAgent(self.memory)
        self.validator = ValidatorAgent(self.memory)

    async def run(self, user_input: UserInput) -> dict:
        """
        执行完整的副业推荐流程

        流程：
        1. 用户理解 → 生成用户画像
        2. 副业匹配 → 推荐 1-3 个副业
        3. 执行规划 → 生成 7 日计划
        4. 验证 → 事实核查
        """
        try:
            # 重置记忆
            self.memory.reset_context()
            self.memory.update_context(
                current_step="user_input",
                user_input=user_input
            )

            # Step 1: 用户理解
            self.memory.update_context(current_step="profiling")
            user_profile = await self.user_profiler.run(user_input)

            # Step 2: 副业匹配
            self.memory.update_context(current_step="matching")
            recommendations = await self.opportunity_miner.run(user_profile)

            if not recommendations:
                return AgentResult(
                    success=False,
                    message="未找到匹配的副业，请尝试调整您的条件"
                ).__dict__

            # 选择最佳推荐
            best_recommendation = recommendations[0]

            # Step 3: 执行规划
            self.memory.update_context(current_step="planning")
            action_plan = await self.action_planner.run(
                user_profile,
                best_recommendation
            )

            # Step 4: 验证
            self.memory.update_context(current_step="validating")
            validation_result = await self.validator.run(
                user_profile,
                best_recommendation,
                action_plan
            )

            # 更新上下文
            self.memory.update_context(
                current_step="completed",
                selected_recommendation=best_recommendation,
                validation_result=validation_result
            )

            # 获取完整上下文
            final_context = self.memory.get_context()

            return AgentResult(
                success=True,
                message="推荐完成",
                data={
                    "user_profile": user_profile.model_dump(),
                    "recommendations": [r.model_dump() for r in recommendations],
                    "selected_recommendation": best_recommendation.model_dump(),
                    "action_plan": action_plan.model_dump(),
                    "validation_result": validation_result.model_dump(),
                }
            ).__dict__

        except Exception as e:
            self.memory.update_context(
                current_step="failed",
                error_message=str(e)
            )
            return AgentResult(
                success=False,
                message=f"执行失败: {str(e)}"
            ).__dict__

    async def run_with_feedback(
        self,
        user_input: UserInput,
        feedback: Literal["success", "failed", "adjust"]
    ) -> dict:
        """
        带反馈的迭代执行

        用户执行结果回流至系统，用于：
        - success: 记录成功经验
        - failed: 分析失败原因并切换备选方案
        - adjust: 调整方案参数
        """
        context = self.memory.get_context()

        if feedback == "success":
            # 记录成功，存入成功案例库
            success_data = {
                "user_profile": context.user_profile,
                "side_hustle": context.selected_recommendation.side_hustle,
                "outcome": "success",
            }
            self.memory.set("success_cases", success_data, agent="feedback")

        elif feedback == "failed":
            # 分析失败原因，切换备选方案
            context = self.memory.get_context()
            recommendations = context.recommendations

            if len(recommendations) > 1:
                # 切换到下一个推荐
                next_recommendation = recommendations[1]
                self.memory.update_context(
                    selected_recommendation=next_recommendation,
                    current_step="replanning"
                )

                # 重新生成计划
                new_plan = await self.action_planner.run(
                    context.user_profile,
                    next_recommendation
                )

                return AgentResult(
                    success=True,
                    message="已切换到备选方案",
                    data={"action_plan": new_plan.model_dump()}
                ).__dict__
            else:
                return AgentResult(
                    success=False,
                    message="所有推荐方案均已尝试，建议调整您的条件"
                ).__dict__

        return AgentResult(
            success=True,
            message="反馈已记录"
        ).__dict__


async def create_side_hustle_recommendation(user_input: UserInput) -> dict:
    """
    快捷函数：创建副业推荐

    用法示例：
    >>> user_input = UserInput(
    ...     city="上海",
    ...     skills=["Python", "Excel"],
    ...     available_time=TimeAvailability.ONE_TO_2H,
    ...     avoid_appearing=True,
    ...     monthly_goal=5000
    ... )
    >>> result = await create_side_hustle_recommendation(user_input)
    """
    orchestrator = SideHustleOrchestrator()
    return await orchestrator.run(user_input)
