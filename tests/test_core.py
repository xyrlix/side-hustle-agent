"""
测试模块
"""

import asyncio
from side_hustle_agent.core.models import UserInput, TimeAvailability, RiskPreference, UserProfile, CityTier
from side_hustle_agent.knowledge import SideHustleDatabase, get_city_data, get_hourly_rate, get_market_density, get_policy_benefits


def test_models():
    """测试数据模型"""
    user_input = UserInput(
        city="上海",
        skills=["Python", "Excel"],
        available_time=TimeAvailability.ONE_TO_2H,
        risk_preference=RiskPreference.MEDIUM,
        avoid_appearing=True,
        monthly_goal=5000
    )
    assert user_input.city == "上海"
    assert user_input.avoid_appearing == True
    print("[PASS] test_models")


def test_city_data():
    """测试城市数据"""
    city = get_city_data("上海")
    assert city is not None
    assert city["tier"] == "一线城市"

    rate = get_hourly_rate("上海", "技术技能")
    assert rate is not None
    assert rate > 0

    density = get_market_density("上海")
    assert isinstance(density, dict)

    policies = get_policy_benefits("上海")
    assert isinstance(policies, list)
    print("[PASS] test_city_data")


def test_side_hustle_database():
    """测试副业数据库"""
    db = SideHustleDatabase()
    hustles = db.get_all()
    assert len(hustles) >= 20, f"Expected at least 20 hustles, got {len(hustles)}"

    # 测试过滤
    filtered = db.filter(requires_appearance=False)
    for h in filtered:
        assert not h.requires_appearance

    # 测试搜索
    results = db.search("电商")
    assert len(results) > 0

    # 测试ID查找
    hustle = db.get_by_id("ai-content-creation")
    assert hustle is not None
    assert hustle.name == "AI 内容代工"
    print("[PASS] test_side_hustle_database")


def test_rules():
    """测试匹配规则逻辑"""
    from side_hustle_agent.agents.opportunity_miner import OpportunityMinerAgent

    # 模拟用户画像
    profile = UserProfile(
        city="上海",
        city_tier=CityTier.FIRST,
        skills=["Python", "Excel"],
        available_hours_per_day=1.5,
        risk_preference=RiskPreference.MEDIUM,
        avoid_appearing=True,
        monthly_goal=5000,
        tags=["一线城市", "有专项技能", "厌恶露脸"],
        hourly_rate_local=120,
        market_density={},
    )

    db = SideHustleDatabase()
    agent = OpportunityMinerAgent(database=db)

    # 测试过滤
    all_hustles = db.get_all()
    filtered = agent._rule_filter(profile, all_hustles)

    # 验证厌恶露脸的过滤
    for h in filtered:
        assert not h.requires_appearance, f"{h.name} requires appearance but user avoids it"

    # 验证时间过滤
    for h in filtered:
        assert h.min_time_hours <= profile.available_hours_per_day, f"{h.name} requires {h.min_time_hours}h but user has {profile.available_hours_per_day}h"

    print(f"[PASS] test_rules - filtered {len(filtered)} hustles from {len(all_hustles)}")


def test_action_plan_generation():
    """测试行动计划的生成"""
    from side_hustle_agent.agents.action_planner import ActionPlannerAgent
    from side_hustle_agent.core.models import Recommendation, SideHustle

    db = SideHustleDatabase()
    hustle = db.get_by_id("ai-content-creation")

    profile = UserProfile(
        city="上海",
        city_tier=CityTier.FIRST,
        skills=["Python"],
        available_hours_per_day=1.5,
        risk_preference=RiskPreference.MEDIUM,
        avoid_appearing=True,
        monthly_goal=5000,
        tags=["一线城市", "有专项技能"],
        hourly_rate_local=120,
        market_density={},
    )

    recommendation = Recommendation(
        side_hustle=hustle,
        match_score=0.85,
        match_reasons=["可以利用您的已有技能", "无需露脸"],
        local_policy_boost=["上海有数字经济扶持"],
    )

    agent = ActionPlannerAgent()
    plan = asyncio.get_event_loop().run_until_complete(
        agent.run(profile, recommendation)
    )

    assert len(plan.day_plans) == 7, f"Expected 7 day plans, got {len(plan.day_plans)}"
    assert plan.success_metrics, "Success metrics should not be empty"
    assert plan.fallback_options, "Fallback options should not be empty"

    print("[PASS] test_action_plan_generation")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print(" Running Tests ")
    print("=" * 50)

    test_models()
    test_city_data()
    test_side_hustle_database()
    test_rules()
    test_action_plan_generation()

    print("=" * 50)
    print(" All Tests Passed! ")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()