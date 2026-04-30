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


class EmploymentStatus(str, Enum):
    """工作状态"""
    EMPLOYED = "在职"
    STUDENT = "学生"
    FREELANCER = "自由职业"
    UNEMPLOYED = "失业"


class WorkMode(str, Enum):
    """工作方式偏好"""
    ONLINE = "线上为主"
    OFFLINE = "线下为主"
    HYBRID = "线上线下结合"


class StartupBudget(str, Enum):
    """启动预算"""
    UNDER_500 = "500元以下"
    FIVE_HUNDRED_TO_2K = "500-2000元"
    TWO_K_TO_5K = "2000-5000元"
    OVER_5K = "5000元以上"


class SideHustleExp(str, Enum):
    """副业经验"""
    NONE = "无经验"
    SOME = "有一些"
    EXPERIENCED = "经验丰富"


class WorkExperience(str, Enum):
    """工作经验"""
    UNDER_1Y = "1年以下"
    ONE_TO_3Y = "1-3年"
    THREE_TO_5Y = "3-5年"
    FIVE_TO_10Y = "5-10年"
    OVER_10Y = "10年以上"


class UserInput(BaseModel):
    """用户输入"""
    name: str | None = None
    city: str = Field(description="所在城市")
    skills: list[str] = Field(default_factory=list, description="拥有的技能，如 Python、Excel、剪辑")
    available_time: TimeAvailability = Field(description="每天可用时间")
    risk_preference: RiskPreference = Field(default=RiskPreference.MEDIUM, description="风险偏好")
    avoid_appearing: bool = Field(default=False, description="是否厌恶露脸")
    monthly_goal: int = Field(default=3000, description="月收入目标，单位：元")
    # 新增字段
    employment_status: EmploymentStatus = Field(default=EmploymentStatus.EMPLOYED, description="工作状态")
    industry: str = Field(default="互联网", description="所在行业")
    work_experience: WorkExperience = Field(default=WorkExperience.ONE_TO_3Y, description="工作经验")
    side_hustle_exp: SideHustleExp = Field(default=SideHustleExp.NONE, description="副业经验")
    startup_budget: StartupBudget = Field(default=StartupBudget.FIVE_HUNDRED_TO_2K, description="启动预算")
    work_mode: WorkMode = Field(default=WorkMode.ONLINE, description="工作方式偏好")


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

    # 新增字段
    employment_status: EmploymentStatus = EmploymentStatus.EMPLOYED
    industry: str = "互联网"
    work_experience: WorkExperience = WorkExperience.ONE_TO_3Y
    side_hustle_exp: SideHustleExp = SideHustleExp.NONE
    startup_budget: StartupBudget = StartupBudget.FIVE_HUNDRED_TO_2K
    work_mode: WorkMode = WorkMode.ONLINE

    # 地域特征
    hourly_rate_local: float = Field(description="本地时薪参考")
    market_density: dict[str, float] = Field(default_factory=dict, description="各类市场密度")
    # 增强分析
    transferable_skills: list[str] = Field(default_factory=list, description="可转化到副业的技能")
    income_realistic_range: dict = Field(default_factory=dict, description="现实收入预期区间")
    recommended_timeline: str = Field(default="", description="推荐启动时间线")
    risk_factors: list[str] = Field(default_factory=list, description="主要风险因素")


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


class ContentStatus(str, Enum):
    """内容状态"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待发布
    PUBLISHED = "published"   # 已发布
    FAILED = "failed"         # 发布失败


class PlatformType(str, Enum):
    """平台类型"""
    WECHAT_PUBLIC = "wechat_public"     # 公众号
    TOUTIAO = "toutiao"                 # 头条号
    XIAOHONGSHU = "xiaohongshu"         # 小红书
    ZHIHU = "zhihu"                     # 知乎
    BAIJIAHAO = "baijiahao"            # 百家号
    BILIBILI = "bilibili"              # B站
    DOUYIN = "douyin"                  # 抖音
    KUAISHOU = "kuaishou"              # 快手
    VIDEO_ACCOUNT = "video_account"   # 视频号


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


# ============================================
# 内容创作模块数据模型
# ============================================

class PlatformInfo(BaseModel):
    """平台信息"""
    id: str
    name: str
    type: PlatformType
    icon: str = ""
    description: str = ""
    content_format: list[str] = Field(default_factory=list, description="支持的内容格式，如 ['text', 'image']")
    max_content_length: int = Field(default=20000, description="最大内容长度")
    features: list[str] = Field(default_factory=list, description="平台特性")


class PlatformAccount(BaseModel):
    """平台账号"""
    id: int = 0
    user_id: int
    platform: PlatformType
    account_name: str = ""
    account_id: str = ""          # 平台上的账号ID
    access_token: str = ""        # 加密存储
    refresh_token: str = ""
    status: str = "active"        # active/suspended/inactive
    followers: int = 0            # 粉丝数
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Content(BaseModel):
    """内容条目"""
    id: int = 0
    user_id: int
    title: str = ""
    body: str = ""                # 主内容（原始版本）
    summary: str = ""             # 摘要
    cover_image: str = ""         # 封面图路径

    # 平台适配版本
    platform_versions: dict[str, str] = Field(default_factory=dict, description="各平台适配内容")

    # 素材关联
    material_ids: list[int] = Field(default_factory=list, description="关联的素材ID列表")

    # 状态和分类
    status: ContentStatus = ContentStatus.DRAFT
    tags: list[str] = Field(default_factory=list, description="内容标签")
    category: str = ""            # 内容分类

    # 发布信息
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    published_platforms: list[str] = Field(default_factory=list, description="已发布的平台列表")

    # AI生成相关
    ai_generated: bool = False
    ai_prompt: str = ""           # 使用的AI提示词

    # 统计
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    revenue: float = 0            # 收益金额

    # 版本控制
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ContentVersion(BaseModel):
    """内容版本历史"""
    id: int = 0
    content_id: int
    version: int
    title: str
    body: str
    change_summary: str = ""      # 变更摘要
    created_at: datetime = Field(default_factory=datetime.now)


class Campaign(BaseModel):
    """运营活动"""
    id: int = 0
    user_id: int
    name: str = ""
    description: str = ""
    content_ids: list[int] = Field(default_factory=list, description="关联的内容ID列表")

    # 活动计划
    start_date: datetime | None = None
    end_date: datetime | None = None

    # 目标
    target_views: int = 0
    target_revenue: float = 0

    # 实际统计
    actual_views: int = 0
    actual_revenue: float = 0

    status: str = "active"       # active/completed/cancelled
    created_at: datetime = Field(default_factory=datetime.now)


class Material(BaseModel):
    """素材（图片、视频、音频）"""
    id: int = 0
    user_id: int
    filename: str = ""
    file_path: str = ""
    file_type: str = ""          # image/video/audio/document
    file_size: int = 0           # 字节
    mime_type: str = ""

    # 元数据
    width: int = 0               # 图片/视频宽度
    height: int = 0             # 图片/视频高度
    duration: int = 0           # 音视频时长（秒）

    # 标签和分组
    tags: list[str] = Field(default_factory=list)
    folder: str = ""             # 素材夹

    created_at: datetime = Field(default_factory=datetime.now)


class PublishLog(BaseModel):
    """发布日志"""
    id: int = 0
    content_id: int
    platform: PlatformType
    status: str = "pending"      # pending/success/failed
    error_message: str = ""
    published_url: str = ""      # 发布的URL
    published_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.now)
