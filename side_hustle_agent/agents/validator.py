"""
验证 Agent
"""

from ..core.memory import SharedMemory
from ..core.models import (
    ActionPlan,
    AgentState,
    Recommendation,
    SideHustle,
    UserProfile,
    ValidationResult,
)
from .base import BaseAgent
from ..prompts import (
    VALIDATOR_SYSTEM,
    VALIDATOR_PROMPT,
)


class ValidatorAgent(BaseAgent):
    """
    验证 Agent

    对输出进行事实核查，包括：
    - 政策时效性
    - 数据合理性
    - 风险提示
    - 可执行性
    """

    def __init__(self, memory: SharedMemory | None = None):
        super().__init__("Validator", memory)

    async def run(
        self,
        user_profile: UserProfile,
        recommendation: Recommendation,
        action_plan: ActionPlan,
    ) -> ValidationResult:
        """
        验证推荐和计划的准确性
        """
        self.update_state(AgentState.RUNNING)

        try:
            warnings = []
            corrections = []
            checked_items = []

            # 1. 检查城市政策
            policy_check = self._check_policy(user_profile)
            checked_items.append(policy_check)
            if policy_check.get("warnings"):
                warnings.extend(policy_check["warnings"])

            # 2. 检查收入预期
            income_check = self._check_income_expectation(user_profile, recommendation)
            checked_items.append(income_check)
            if income_check.get("warnings"):
                warnings.extend(income_check["warnings"])

            # 3. 检查时间可行性
            time_check = self._check_time_feasibility(action_plan)
            checked_items.append(time_check)
            if time_check.get("corrections"):
                corrections.extend(time_check["corrections"])

            # 4. 检查平台规则
            platform_check = self._check_platform_rules(recommendation.side_hustle)
            checked_items.append(platform_check)
            if platform_check.get("warnings"):
                warnings.extend(platform_check["warnings"])

            # 5. 检查风险提示完整性
            risk_check = self._check_risk_completeness(recommendation, action_plan)
            checked_items.append(risk_check)
            if risk_check.get("corrections"):
                corrections.extend(risk_check["corrections"])

            is_valid = len(corrections) == 0

            result = ValidationResult(
                is_valid=is_valid,
                checked_items=checked_items,
                warnings=warnings,
                corrections=corrections,
            )

            # 存入记忆
            self.memory.set("validation_result", result.model_dump(), agent=self.name)
            self.memory.update_context(validation_result=result)

            self.update_state(AgentState.COMPLETED)
            return result

        except Exception as e:
            self.update_state(AgentState.FAILED)
            self.memory.update_context(error_message=str(e))
            raise

    def _check_policy(self, profile: UserProfile) -> dict:
        """检查政策时效性"""
        warnings = []
        city = profile.city

        # 简化检查，实际应查询实时政策
        policy_benefits_known = {
            "上海": ["灵活就业补贴", "数字经济扶持"],
            "北京": ["创业担保贷款", "灵活就业社保补贴"],
            "杭州": ["电商创业扶持", "数字经济补贴"],
            "成都": ["灵活就业登记", "技能培训补贴"],
        }

        city_policies = policy_benefits_known.get(city, [])
        if not city_policies:
            warnings.append(f"未找到{city}的当前政策信息，建议咨询当地人社部门获取最新政策")

        return {
            "check_type": "policy",
            "is_valid": True,
            "warnings": warnings,
        }

    def _check_income_expectation(self, profile: UserProfile, recommendation: Recommendation) -> dict:
        """检查收入预期"""
        warnings = []
        hustle = recommendation.side_hustle
        target = profile.monthly_goal

        # 收入潜力检查
        if hustle.income_potential < target:
            warnings.append(
                f"警告：{hustle.name}的收入潜力({hustle.income_potential}元)低于您的目标({target}元)，"
                f"可能需要调整预期或选择其他副业"
            )

        # 启动成本与目标关系
        if hustle.startup_cost > target * 0.5:
            warnings.append(
                f"注意：{hustle.name}的启动成本({hustle.startup_cost}元)较高，"
                f"建议确认资金充足后再投入"
            )

        return {
            "check_type": "income",
            "is_valid": len(warnings) == 0,
            "warnings": warnings,
        }

    def _check_time_feasibility(self, action_plan: ActionPlan) -> dict:
        """检查时间可行性"""
        corrections = []
        hustle = action_plan.side_hustle

        # 检查每日计划的时间安排
        for day_plan in action_plan.day_plans:
            if len(day_plan.tasks) > 5:
                corrections.append(
                    f"Day {day_plan.day} 的任务安排过多({len(day_plan.tasks)}项)，"
                    f"建议拆分为更小的步骤"
                )

        # 检查难度递进
        task_counts = [len(dp.tasks) for dp in action_plan.day_plans]
        if task_counts and task_counts[0] < task_counts[-1] * 0.5:
            corrections.append(
                "Day 1-2 的任务量相对较少，建议适当增加入门难度，"
                "帮助您更快进入状态"
            )

        return {
            "check_type": "time",
            "is_valid": len(corrections) == 0,
            "corrections": corrections,
        }

    def _check_platform_rules(self, hustle: SideHustle) -> dict:
        """检查平台规则"""
        warnings = []

        if not hustle.platform_rules:
            warnings.append(
                f"{hustle.name}的平台规则信息不完整，"
                f"建议在开始前仔细阅读相关平台的用户协议"
            )

        # 敏感品类检查
        sensitive_keywords = ["医疗", "金融", "投资", "代运营"]
        for rule in hustle.platform_rules:
            for keyword in sensitive_keywords:
                if keyword in rule:
                    warnings.append(
                        f"{hustle.name}涉及{keyword}相关领域，"
                        f"需特别注意合规要求"
                    )

        return {
            "check_type": "platform",
            "is_valid": len(warnings) == 0,
            "warnings": warnings,
        }

    def _check_risk_completeness(self, recommendation: Recommendation, action_plan: ActionPlan) -> dict:
        """检查风险提示完整性"""
        corrections = []
        hustle = recommendation.side_hustle

        # 检查是否缺少重要风险提示
        existing_risks = set()
        for risk in hustle.policy_risks:
            existing_risks.add(risk)

        # 常见但未提及的风险
        common_risks = {
            "requires_appearance": "需要露脸的副业可能影响您的隐私",
            "high_startup": "启动成本较高可能导致资金压力",
            "seasonal": "部分副业有季节性，需提前规划",
        }

        if not hustle.policy_risks and not existing_risks:
            corrections.append(
                f"{hustle.name}的风险提示较少，建议自行了解可能的风险，"
                f"并做好应对预案"
            )

        # 检查是否有备选方案
        if not action_plan.fallback_options or len(action_plan.fallback_options) < 2:
            corrections.append(
                "备选方案较少，建议准备 2-3 个备选副业以应对主方案不可行的情况"
            )

        return {
            "check_type": "risk",
            "is_valid": len(corrections) == 0,
            "corrections": corrections,
        }
