"""
数据模型定义
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, Field


class CityTier(str, Enum):
    """城市等级"""
    FIRST = "一线城市"
    SECOND = "二线城市"
    THIRD = "三线城市"
    FOURTH = "四线及以下"


class RiskPreference(str, Enum):
    """风险偏好"""
    LOW = "保守型"
    MEDIUM = "稳健型"
    HIGH = "进取型"


class TimeAvailability(str, Enum):
    """可用时间"""
    LESS_1H = "每天少于1小时"
    ONE_TO_2H = "每天1-2小时"
    TWO_TO_4H = "每天2-4小时"
    MORE_4H = "每天4小时以上"


class SkillLevel(str, Enum):
    """技能水平"""
    NONE = "无特殊技能"
    BASIC = "基础技能"
    INTERMEDIATE = "中级技能"
    ADVANCED = "高级技能"


class UserInput(BaseModel):
    """用户输入"""
    name: str | None = None
    city: str = Field(description="所在城市")
    skills: list[str] = Field(default_factory=list, description="拥有的技能，如 Python、Excel、剪辑")
    available_time: TimeAvailability = Field(description="每天可用时间")
    risk_preference: RiskPreference = Field(default=RiskPreference.MEDIUM, description="风险偏好")
    avoid_appearing: bool = Field(default=False, description="是否厌恶露脸")
    monthly_goal: int = Field(default=3000, description="月收入目标，单位：元")


class UserProfile(BaseModel):
    """用户画像"""
    city: str
    city_tier: CityTier
    skills: list[str]
    available_hours_per_day: float  # 转换为小时数
    risk_preference: RiskPreference
    avoid_appearing: bool
    monthly_goal: int
    tags: list[str] = Field(default_factory=list, description="画像标签")

    # 地域特征
    hourly_rate_local: float = Field(description="本地时薪参考")
    market_density: dict[str, float] = Field(default_factory=dict, description="各类市场密度")


class SideHustle(BaseModel):
    """副业条目"""
    id: str
    name: str
    description: str
    startup_cost: Annotated[int, Field(description="启动成本，单位：元")]
    learning_curve: SkillLevel
    platform_rules: list[str] = Field(default_factory=list, description="主要平台规则要点")
    recent_cases: list[dict] = Field(default_factory=list, description="近期变现案例")
    policy_risks: list[str] = Field(default_factory=list, description="政策风险")
    policy_benefits: list[str] = Field(default_factory=list, description="政策福利支持")

    # 匹配条件
    min_time_hours: float = Field(description="最低时间要求（小时/天）")
    requires_appearance: bool = Field(description="是否需要露脸")
    location_requirements: list[str] = Field(default_factory=list, description="地域要求")

    # 评估维度
    income_potential: Annotated[int, Field(description="月收入潜力上限，元")]
    scalability: Annotated[int, Field(ge=1, le=5, description="可扩展性 1-5")]
    stability: Annotated[int, Field(ge=1, le=5, description="稳定性 1-5")]


class Recommendation(BaseModel):
    """副业推荐"""
    side_hustle: SideHustle
    match_score: Annotated[float, Field(ge=0, le=1, description="匹配度 0-1")]
    match_reasons: list[str] = Field(default_factory=list, description="匹配原因")
    local_policy_boost: list[str] = Field(default_factory=list, description="本地政策加成")


class DayPlan(BaseModel):
    """单日计划"""
    day: int = Field(ge=1, le=7)
    title: str
    tasks: list[str]
    ai_prompts: dict[str, str] | None = Field(default=None, description="AI 提示词模板")
    templates: dict[str, str] | None = Field(default=None, description="话术/文案模板")


class ActionPlan(BaseModel):
    """执行规划"""
    side_hustle: SideHustle
    day_plans: list[DayPlan] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list, description="成功指标")
    fallback_options: list[str] = Field(default_factory=list, description="备选方案")
    tips: list[str] = Field(default_factory=list, description="注意事项")


class ValidationResult(BaseModel):
    """验证结果"""
    is_valid: bool
    checked_items: list[dict] = Field(default_factory=list, description="检查项详情")
    warnings: list[str] = Field(default_factory=list, description="警告信息")
    corrections: list[str] = Field(default_factory=list, description="修正建议")


class AgentState(str, Enum):
    """Agent 状态"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MemoryEntry(BaseModel):
    """记忆条目"""
    agent: str
    key: str
    value: Any
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationContext(BaseModel):
    """对话上下文"""
    user_id: str | None = None
    session_id: str | None = None
    current_step: str = "user_input"
    user_input: UserInput | None = None
    user_profile: UserProfile | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    selected_recommendation: Recommendation | None = None
    action_plan: ActionPlan | None = None
    validation_result: ValidationResult | None = None
    error_message: str | None = None
