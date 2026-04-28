"""
副业知识图谱 Agent
"""

import json
from typing import Any

from ..core.memory import SharedMemory
from ..core.models import (
    AgentState,
    CityTier,
    Recommendation,
    SideHustle,
    UserProfile,
)
from .base import BaseAgent
from ..knowledge import SideHustleDatabase, get_side_hustle_database, get_policy_benefits, get_market_density
from ..prompts import (
    OPPORTUNITY_MINER_SYSTEM,
    OPPORTUNITY_MINER_PROMPT,
)


class OpportunityMinerAgent(BaseAgent):
    """
    副业知识图谱 Agent

    使用内置动态知识库和长链推理判断适配性，
    输出与用户画像匹配的副业推荐列表。
    """

    def __init__(self, memory: SharedMemory | None = None, database: SideHustleDatabase | None = None):
        super().__init__("OpportunityMiner", memory)
        self.database = database or get_side_hustle_database()

    async def run(self, user_profile: UserProfile) -> list[Recommendation]:
        """
        根据用户画像匹配副业
        """
        self.update_state(AgentState.RUNNING)

        try:
            # 获取所有副业
            all_hustles = self.database.get_all()

            # 规则过滤（快速排除明显不匹配的）
            filtered_hustles = self._rule_filter(user_profile, all_hustles)

            # 计算匹配度
            recommendations = []
            for hustle in filtered_hustles:
                rec = self._calculate_match(user_profile, hustle)
                recommendations.append(rec)

            # 按匹配度排序
            recommendations.sort(key=lambda x: x.match_score, reverse=True)

            # 取 Top 3
            top_recommendations = recommendations[:3]

            # 存入记忆
            self.memory.set(
                "recommendations",
                [rec.model_dump() for rec in top_recommendations],
                agent=self.name
            )
            self.memory.update_context(recommendations=top_recommendations)

            self.update_state(AgentState.COMPLETED)
            return top_recommendations

        except Exception as e:
            self.update_state(AgentState.FAILED)
            self.memory.update_context(error_message=str(e))
            raise

    def _rule_filter(self, profile: UserProfile, hustles: list[SideHustle]) -> list[SideHustle]:
        """基于规则的快速过滤"""
        results = []

        for h in hustles:
            # 时间过滤
            if h.min_time_hours > profile.available_hours_per_day:
                continue

            # 露脸偏好过滤
            if profile.avoid_appearing and h.requires_appearance:
                continue

            # 启动成本过滤（保守型用户限制更高）
            if profile.risk_preference.value == "保守型" and h.startup_cost > 2000:
                continue
            elif profile.risk_preference.value == "稳健型" and h.startup_cost > 5000:
                continue

            # 城市等级过滤
            if profile.city_tier == CityTier.FOURTH:
                if "一线城市" in h.location_requirements or h.startup_cost > 2000:
                    continue

            results.append(h)

        return results

    def _calculate_match(self, profile: UserProfile, hustle: SideHustle) -> Recommendation:
        """计算匹配度"""
        score = 0.5  # 基础分
        reasons = []
        policy_boost = []

        # 时间匹配
        if hustle.min_time_hours <= profile.available_hours_per_day * 0.7:
            score += 0.15
            reasons.append("时间要求宽松，契合您的作息")
        elif hustle.min_time_hours <= profile.available_hours_per_day:
            score += 0.05
            reasons.append("时间要求基本满足")

        # 技能匹配
        if profile.skills:
            skill_match = any(
                skill.lower() in hustle.description.lower()
                or skill.lower() in hustle.name.lower()
                for skill in profile.skills
            )
            if skill_match:
                score += 0.15
                reasons.append("可以利用您的已有技能")

        # 收入潜力匹配
        if hustle.income_potential >= profile.monthly_goal:
            score += 0.1
            reasons.append(f"收入潜力({hustle.income_potential}元)可达标")
        elif hustle.income_potential >= profile.monthly_goal * 0.7:
            score += 0.05

        # 稳定性匹配
        if profile.risk_preference.value == "保守型" and hustle.stability >= 4:
            score += 0.1
            reasons.append("稳定性较高，适合保守型用户")

        # 城市政策加成
        city_policies = get_policy_benefits(profile.city)
        if city_policies:
            # 检查副业是否与城市政策相关
            for policy in city_policies:
                if any(keyword in hustle.name or keyword in hustle.description
                       for keyword in ["电商", "数字", "内容", "技术"]):
                    if "电商" in policy or "数字" in policy or "创业" in policy:
                        policy_boost.append(f"{profile.city}有{policy}支持")
                        break

        # 露脸偏好
        if profile.avoid_appearing and not hustle.requires_appearance:
            score += 0.1
            reasons.append("无需露脸，符合您的偏好")

        # 确保分数不超过 1.0
        score = min(score, 1.0)

        return Recommendation(
            side_hustle=hustle,
            match_score=round(score, 2),
            match_reasons=reasons,
            local_policy_boost=policy_boost,
        )