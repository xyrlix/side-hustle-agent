"""
副业雷达 CLI 工具

提供命令行界面快速测试副业推荐功能。
"""

import asyncio
import json
import sys

from .core.models import UserInput, TimeAvailability, RiskPreference
from .orchestrator import SideHustleOrchestrator


async def interactive_mode():
    """交互模式"""
    print("=" * 50)
    print("  副业雷达 - 多智能体副业推荐系统")
    print("=" * 50)
    print()

    # 收集用户输入
    city = input("所在城市: ").strip() or "上海"

    skills_input = input("拥有技能 (用逗号分隔，直接回车跳过): ").strip()
    skills = [s.strip() for s in skills_input.split(",") if s.strip()] if skills_input else []

    print("\n可用时间选项:")
    print("  1. 每天少于1小时")
    print("  2. 每天1-2小时")
    print("  3. 每天2-4小时")
    print("  4. 每天4小时以上")
    time_choice = input("选择 (1-4): ").strip() or "2"
    time_map = {"1": TimeAvailability.LESS_1H, "2": TimeAvailability.ONE_TO_2H,
                "3": TimeAvailability.TWO_TO_4H, "4": TimeAvailability.MORE_4H}
    available_time = time_map.get(time_choice, TimeAvailability.ONE_TO_2H)

    print("\n风险偏好选项:")
    print("  1. 保守型")
    print("  2. 稳健型")
    print("  3. 进取型")
    risk_choice = input("选择 (1-3): ").strip() or "2"
    risk_map = {"1": RiskPreference.LOW, "2": RiskPreference.MEDIUM, "3": RiskPreference.HIGH}
    risk_preference = risk_map.get(risk_choice, RiskPreference.MEDIUM)

    avoid_appearing_input = input("厌恶露脸? (y/N): ").strip().lower()
    avoid_appearing = avoid_appearing_input == "y"

    monthly_goal_input = input("月收入目标 (元): ").strip()
    monthly_goal = int(monthly_goal_input) if monthly_goal_input.isdigit() else 3000

    # 构建用户输入
    user_input = UserInput(
        city=city,
        skills=skills,
        available_time=available_time,
        risk_preference=risk_preference,
        avoid_appearing=avoid_appearing,
        monthly_goal=monthly_goal,
    )

    print("\n" + "-" * 50)
    print("正在分析您的画像...")
    print()

    # 执行推荐
    orchestrator = SideHustleOrchestrator()
    result = await orchestrator.run(user_input)

    # 输出结果
    if result["success"]:
        data = result["data"]
        print("✅ 推荐完成!")
        print()

        # 用户画像
        profile = data["user_profile"]
        print(f"📊 您的画像:")
        print(f"   城市: {profile['city']} ({profile['city_tier']})")
        print(f"   技能: {', '.join(profile['skills']) or '无特殊技能'}")
        print(f"   时间: 每天 {profile['available_hours_per_day']} 小时")
        print(f"   标签: {', '.join(profile['tags'])}")
        print()

        # 推荐结果
        recommendations = data["recommendations"]
        print(f"📋 推荐了 {len(recommendations)} 个副业:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. {rec['side_hustle']['name']}")
            print(f"     匹配度: {rec['match_score']:.0%}")
            print(f"     {rec['side_hustle']['description'][:50]}...")
            print(f"     匹配原因: {', '.join(rec['match_reasons'][:2])}")

        print()

        # 行动计划
        plan = data["action_plan"]
        print(f"📅 7日启动计划:")
        for day_plan in plan["day_plans"]:
            print(f"\n  Day {day_plan['day']}: {day_plan['title']}")
            for task in day_plan["tasks"][:2]:
                print(f"     - {task}")

        # 验证结果
        validation = data["validation_result"]
        if validation["warnings"]:
            print("\n⚠️  注意事项:")
            for warning in validation["warnings"][:2]:
                print(f"   - {warning}")

    else:
        print(f"❌ 推荐失败: {result['message']}")

    print()
    print("-" * 50)


def main():
    """主入口"""
    asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()