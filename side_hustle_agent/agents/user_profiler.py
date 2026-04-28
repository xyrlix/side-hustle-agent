"""
用户理解 Agent
"""

import json

from ..core.memory import SharedMemory
from ..core.models import (
    AgentState,
    CityTier,
    RiskPreference,
    SideHustle,
    TimeAvailability,
    UserInput,
    UserProfile,
)
from .base import BaseAgent
from ..knowledge import get_city_data, get_city_tier, get_hourly_rate, get_market_density
from ..prompts import (
    USER_PROFILER_SYSTEM,
    USER_PROFILER_PROMPT,
)


class UserProfilerAgent(BaseAgent):
    """
    用户理解 Agent

    输入：用户填写的简表
    动作：调用 LLM 进行意图解析 + 地域经济数据匹配
    输出：结构化用户画像标签
    """

    def __init__(self, memory: SharedMemory | None = None):
        super().__init__("UserProfiler", memory)

    async def run(self, user_input: UserInput) -> UserProfile:
        """
        分析用户输入，生成用户画像
        """
        self.update_state(AgentState.RUNNING)

        try:
            # 获取城市数据
            city_data = get_city_data(user_input.city)

            # 解析城市等级
            city_tier = self._parse_city_tier(city_data)

            # 估算本地时薪
            hourly_rate = self._estimate_hourly_rate(
                user_input.city, user_input.skills
            )

            # 计算每日可用小时数
            hours_per_day = self._time_to_hours(user_input.available_time)

            # 获取市场密度
            market_density = get_market_density(user_input.city)

            # 调用 LLM 增强分析
            prompt = USER_PROFILER_PROMPT.format(
                city=user_input.city,
                skills=", ".join(user_input.skills) if user_input.skills else "无",
                available_time=user_input.available_time.value,
                risk_preference=user_input.risk_preference.value,
                avoid_appearing="是" if user_input.avoid_appearing else "否",
                monthly_goal=user_input.monthly_goal,
            )

            response = await self.think_async(prompt, USER_PROFILER_SYSTEM)

            # 解析响应，生成画像标签
            tags = self._extract_tags(user_input, city_tier)

            profile = UserProfile(
                city=user_input.city,
                city_tier=city_tier,
                skills=user_input.skills,
                available_hours_per_day=hours_per_day,
                risk_preference=user_input.risk_preference,
                avoid_appearing=user_input.avoid_appearing,
                monthly_goal=user_input.monthly_goal,
                tags=tags,
                hourly_rate_local=hourly_rate,
                market_density=market_density,
            )

            # 存入记忆
            self.memory.set("user_profile", profile.model_dump(), agent=self.name)
            self.memory.update_context(user_profile=profile)

            self.update_state(AgentState.COMPLETED)
            return profile

        except Exception as e:
            self.update_state(AgentState.FAILED)
            self.memory.update_context(error_message=str(e))
            raise

    def _parse_city_tier(self, city_data: dict | None) -> CityTier:
        """从城市数据解析城市等级"""
        if city_data is None:
            return CityTier.THIRD

        tier_str = city_data.get("tier", "三线城市")
        if tier_str == "一线城市":
            return CityTier.FIRST
        elif tier_str == "二线城市":
            return CityTier.SECOND
        elif tier_str == "三线城市":
            return CityTier.THIRD
        else:
            return CityTier.FOURTH

    def _estimate_hourly_rate(self, city: str, skills: list[str]) -> float:
        """估算本地时薪"""
        # 根据技能确定类别
        skill_category = "基础技能"
        for skill in skills:
            if skill in ["Python", "JavaScript", "Java", "Go", "SQL", "AI", "大数据"]:
                skill_category = "技术技能"
                break
            elif skill in ["设计", "UI", "UX", "美工", "平面设计"]:
                skill_category = "设计技能"
                break
            elif skill in ["英语", "日语", "韩语", "翻译", "口译"]:
                skill_category = "语言技能"
                break
            elif skill in ["Excel", "PPT", "Word", "办公", "行政"]:
                skill_category = "办公技能"
                break

        rate = get_hourly_rate(city, skill_category)
        return rate if rate else 50.0

    def _time_to_hours(self, time_avail: TimeAvailability) -> float:
        """将时间枚举转换为小时数"""
        mapping = {
            TimeAvailability.LESS_1H: 0.5,
            TimeAvailability.ONE_TO_2H: 1.5,
            TimeAvailability.TWO_TO_4H: 3.0,
            TimeAvailability.MORE_4H: 5.0,
        }
        return mapping.get(time_avail, 1.5)

    def _extract_tags(self, user_input: UserInput, city_tier: CityTier) -> list[str]:
        """提取用户画像标签"""
        tags = []

        # 城市标签
        if city_tier == CityTier.FIRST:
            tags.append("一线城市")
        elif city_tier == CityTier.SECOND:
            tags.append("二线城市")
        elif city_tier == CityTier.THIRD:
            tags.append("三线城市")
        else:
            tags.append("四线及以下")

        # 时间标签
        if user_input.available_time == TimeAvailability.LESS_1H:
            tags.append("时间紧张")
        elif user_input.available_time == TimeAvailability.ONE_TO_2H:
            tags.append("碎片时间")
        elif user_input.available_time == TimeAvailability.TWO_TO_4H:
            tags.append("时间充裕")
        else:
            tags.append("时间自由")

        # 技能标签
        if user_input.skills:
            tags.append("有专项技能")
        else:
            tags.append("无特殊技能")

        # 露脸偏好
        if user_input.avoid_appearing:
            tags.append("厌恶露脸")

        # 风险偏好
        if user_input.risk_preference == RiskPreference.LOW:
            tags.append("保守型")
        elif user_input.risk_preference == RiskPreference.HIGH:
            tags.append("进取型")
        else:
            tags.append("稳健型")

        # 目标标签
        if user_input.monthly_goal >= 8000:
            tags.append("高目标")
        elif user_input.monthly_goal >= 4000:
            tags.append("中目标")
        elif user_input.monthly_goal <= 2000:
            tags.append("低目标")

        return tags