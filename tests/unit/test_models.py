"""
数据模型单元测试
"""

import pytest
from side_hustle_agent.core.models import (
    UserInput, UserProfile, SideHustle, Recommendation, ActionPlan, DayPlan,
    Content, ContentVersion, Campaign, PlatformAccount, Material, PublishLog,
    ContentStatus, PlatformType, CityTier, RiskPreference, TimeAvailability,
    SkillLevel, EmploymentStatus, WorkMode, StartupBudget, SideHustleExp, WorkExperience
)


class TestEnums:
    """测试枚举类型"""

    def test_city_tier(self):
        assert CityTier.FIRST == "一线城市"
        assert CityTier.SECOND == "二线城市"
        assert CityTier.THIRD == "三线城市"
        assert CityTier.FOURTH == "四线及以下"

    def test_risk_preference(self):
        assert RiskPreference.LOW == "保守型"
        assert RiskPreference.MEDIUM == "稳健型"
        assert RiskPreference.HIGH == "进取型"

    def test_time_availability(self):
        assert TimeAvailability.LESS_1H == "每天少于1小时"
        assert TimeAvailability.ONE_TO_2H == "每天1-2小时"
        assert TimeAvailability.TWO_TO_4H == "每天2-4小时"
        assert TimeAvailability.MORE_4H == "每天4小时以上"

    def test_content_status(self):
        assert ContentStatus.DRAFT == "draft"
        assert ContentStatus.PENDING == "pending"
        assert ContentStatus.PUBLISHED == "published"
        assert ContentStatus.FAILED == "failed"

    def test_platform_type(self):
        assert PlatformType.WECHAT_PUBLIC == "wechat_public"
        assert PlatformType.TOUTIAO == "toutiao"
        assert PlatformType.XIAOHONGSHU == "xiaohongshu"
        assert PlatformType.ZHIHU == "zhihu"


class TestUserInput:
    """测试用户输入模型"""

    def test_default_values(self):
        user_input = UserInput(
            city="北京",
            available_time=TimeAvailability.ONE_TO_2H
        )
        assert user_input.city == "北京"
        assert user_input.risk_preference == RiskPreference.MEDIUM
        assert user_input.avoid_appearing == False
        assert user_input.monthly_goal == 3000

    def test_full_values(self, sample_user_input):
        assert sample_user_input.city == "上海"
        assert "Python" in sample_user_input.skills
        assert sample_user_input.risk_preference == RiskPreference.MEDIUM

    def test_validation(self):
        # 测试有效数据
        user_input = UserInput(
            city="深圳",
            skills=["JavaScript", "React"],
            available_time=TimeAvailability.TWO_TO_4H,
            monthly_goal=10000
        )
        assert user_input.city == "深圳"
        assert len(user_input.skills) == 2
        assert user_input.monthly_goal == 10000


class TestContent:
    """测试内容模型"""

    def test_content_creation(self):
        content = Content(
            id=1,
            user_id=100,
            title="测试标题",
            body="测试正文内容",
            summary="摘要",
            status=ContentStatus.DRAFT
        )
        assert content.title == "测试标题"
        assert content.status == ContentStatus.DRAFT
        assert content.views == 0

    def test_content_defaults(self):
        content = Content(user_id=1, title="默认标题")
        assert content.body == ""
        assert content.tags == []
        assert content.platform_versions == {}
        assert content.status == ContentStatus.DRAFT

    def test_content_status_transition(self):
        content = Content(user_id=1, title="Test", status=ContentStatus.DRAFT)
        assert content.status == ContentStatus.DRAFT

        content.status = ContentStatus.PENDING
        assert content.status == ContentStatus.PENDING

        content.status = ContentStatus.PUBLISHED
        assert content.status == ContentStatus.PUBLISHED


class TestSideHustle:
    """测试副业条目模型"""

    def test_side_hustle_creation(self):
        hustle = SideHustle(
            id="test-hustle",
            name="测试副业",
            description="这是一个测试副业",
            startup_cost=1000,
            learning_curve=SkillLevel.INTERMEDIATE,
            min_time_hours=1.5,
            requires_appearance=False,
            income_potential=8000,
            scalability=4,
            stability=3
        )
        assert hustle.name == "测试副业"
        assert hustle.startup_cost == 1000
        assert hustle.requires_appearance == False

    def test_side_hustle_validation(self):
        # 测试有效性边界
        hustle = SideHustle(
            id="valid-hustle",
            name="Valid",
            description="Test",
            startup_cost=0,  # 允许0启动成本
            learning_curve=SkillLevel.BASIC,
            min_time_hours=0.5,
            requires_appearance=True,
            income_potential=50000,
            scalability=5,
            stability=5
        )
        assert hustle.scalability == 5
        assert hustle.stability == 5


class TestActionPlan:
    """测试行动计划模型"""

    def test_day_plan_creation(self):
        day_plan = DayPlan(
            day=1,
            title="第一天",
            tasks=["任务1", "任务2", "任务3"]
        )
        assert day_plan.day == 1
        assert len(day_plan.tasks) == 3

    def test_action_plan_with_days(self):
        day_plans = [
            DayPlan(day=i, title=f"Day {i}", tasks=[f"Task {i}"])
            for i in range(1, 8)
        ]

        action_plan = ActionPlan(
            side_hustle=SideHustle(
                id="test", name="Test", description="Test",
                startup_cost=500, learning_curve=SkillLevel.BASIC,
                min_time_hours=1, requires_appearance=False,
                income_potential=5000, scalability=3, stability=3
            ),
            day_plans=day_plans,
            success_metrics=["Metric1", "Metric2"],
            fallback_options=["Fallback1"]
        )

        assert len(action_plan.day_plans) == 7
        assert len(action_plan.success_metrics) == 2