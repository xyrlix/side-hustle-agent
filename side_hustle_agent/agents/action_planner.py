"""
执行规划 Agent
"""

import json

from ..core.memory import SharedMemory
from ..core.models import (
    ActionPlan,
    AgentState,
    DayPlan,
    Recommendation,
    SideHustle,
    UserProfile,
)
from .base import BaseAgent
from ..prompts import (
    ACTION_PLANNER_SYSTEM,
    ACTION_PLANNER_PROMPT,
)


class ActionPlannerAgent(BaseAgent):
    """
    执行规划 Agent

    针对推荐的副业，生成 7 日启动计划，
    包含每日任务、AI 提示词模板、话术示例等。
    """

    def __init__(self, memory: SharedMemory | None = None):
        super().__init__("ActionPlanner", memory)

    async def run(
        self,
        user_profile: UserProfile,
        recommendation: Recommendation
    ) -> ActionPlan:
        """
        生成执行计划
        """
        self.update_state(AgentState.RUNNING)

        try:
            hustle = recommendation.side_hustle

            # 根据不同副业类型生成不同的计划模板
            if "ai" in hustle.id.lower() or "内容" in hustle.name:
                day_plans = self._generate_content_plan(hustle, user_profile)
            elif "电商" in hustle.name or "闲鱼" in hustle.description:
                day_plans = self._generate_ecommerce_plan(hustle, user_profile)
            elif "剪辑" in hustle.name or "视频" in hustle.name:
                day_plans = self._generate_video_plan(hustle, user_profile)
            elif "模板" in hustle.name or "设计" in hustle.name:
                day_plans = self._generate_template_plan(hustle, user_profile)
            elif "服务" in hustle.name or "助理" in hustle.name:
                day_plans = self._generate_service_plan(hustle, user_profile)
            else:
                day_plans = self._generate_generic_plan(hustle, user_profile)

            action_plan = ActionPlan(
                side_hustle=hustle,
                day_plans=day_plans,
                success_metrics=self._get_success_metrics(hustle),
                fallback_options=self._get_fallback_options(hustle),
                tips=self._get_tips(hustle),
            )

            # 存入记忆
            self.memory.set("action_plan", action_plan.model_dump(), agent=self.name)
            self.memory.update_context(action_plan=action_plan)

            self.update_state(AgentState.COMPLETED)
            return action_plan

        except Exception as e:
            self.update_state(AgentState.FAILED)
            self.memory.update_context(error_message=str(e))
            raise

    def _generate_content_plan(self, hustle: SideHustle, profile: UserProfile) -> list[DayPlan]:
        """AI 内容代工 7 日计划"""
        return [
            DayPlan(
                day=1,
                title="平台注册与定位",
                tasks=[
                    "注册 2-3 个内容平台账号（知乎、小红书、公众号）",
                    "完善个人资料，定位细分领域",
                    "研究同领域头部账号的内容风格",
                ],
                ai_prompts={
                    "账号简介": "你是一位专注于{领域}的资深内容创作者，请为我生成一段简洁有力的账号简介，100字以内，包含专业背书和价值承诺。"
                },
            ),
            DayPlan(
                day=2,
                title="制作第一篇内容",
                tasks=[
                    "确定第一篇文章/帖子主题",
                    "使用 AI 工具生成初稿",
                    "人工优化和润色",
                ],
                ai_prompts={
                    "文章生成": "请以专业但不晦涩的风格，撰写一篇关于{主题}的{字数}字文章，要求：1) 开头有吸引力 2) 有2-3个具体案例 3) 结尾有行动指引",
                    "标题优化": "为文章《{原标题}》生成5个更具吸引力的标题选项"
                },
                templates={
                    "发布话术": "大家好，我是{名字}，今天分享{主题}的实战经验..."
                }
            ),
            DayPlan(
                day=3,
                title="发布与数据观察",
                tasks=[
                    "在主平台发布第一篇内容",
                    "同步到其他平台",
                    "观察 24 小时内的数据反馈",
                ],
            ),
            DayPlan(
                day=4,
                title="复盘与优化",
                tasks=[
                    "分析第一篇内容的阅读量、互动率",
                    "根据数据调整内容方向",
                    "制定本周内容计划",
                ],
            ),
            DayPlan(
                day=5,
                title="建立稳定产出节奏",
                tasks=[
                    "确定内容发布频率（如每周 3 篇）",
                    "建立内容素材库",
                    "开始第二条内容的创作",
                ],
            ),
            DayPlan(
                day=6,
                title="尝试变现路径",
                tasks=[
                    "了解平台的变现方式（赞赏、付费专栏、品牌合作）",
                    "设置收款方式",
                    "尝试接第一单",
                ],
            ),
            DayPlan(
                day=7,
                title="建立常态化运营",
                tasks=[
                    "复盘本周运营数据",
                    "优化工作流程",
                    "规划下周目标",
                ],
                templates={
                    "复盘模板": "本周发布{数量}篇，总阅读{阅读量}，互动{互动量}，变现{金额}元"
                }
            ),
        ]

    def _generate_ecommerce_plan(self, hustle: SideHustle, profile: UserProfile) -> list[DayPlan]:
        """无货源电商 7 日计划"""
        return [
            DayPlan(
                day=1,
                title="平台选择与账号准备",
                tasks=[
                    "选择主战平台（闲鱼/拼多多/抖音小店）",
                    "注册账号并完成实名认证",
                    "研究平台规则和禁售品类",
                ],
                templates={
                    "账号设置": "昵称建议：好物优选+城市名，增加地域信任感"
                }
            ),
            DayPlan(
                day=2,
                title="选品与货源对接",
                tasks=[
                    "确定目标品类（建议从家居/数码配件入手）",
                    "在 1688/拼多多批发网寻找优质货源",
                    "比较价格和物流时效",
                ],
                ai_prompts={
                    "选品分析": "分析当前闲鱼上{品类}的热销款式，列出TOP5及各自优势"
                },
            ),
            DayPlan(
                day=3,
                title="商品上架与优化",
                tasks=[
                    "上架第一批 5-10 个商品",
                    "优化商品标题和描述",
                    "添加真实感强的图片",
                ],
                templates={
                    "标题模板": "全新【品牌】{商品名称}，因{原因}转让，限时{价格}，可小刀",
                    "描述模板": "商品来源：{来源} | 购买时间：{时间} | 新旧程度：{程度}\n转让原因：{原因}\n售后说明：{售后}"
                }
            ),
            DayPlan(
                day=4,
                title="发布与获客",
                tasks=[
                    "发布第一批商品",
                    "在相关话题下发帖引流",
                    "开始第一批咨询的回复",
                ],
                templates={
                    "回复话术": "亲，感谢咨询！{商品}现价{价格}，今天拍下可以{优惠}，快递{天数}天内发出~"
                }
            ),
            DayPlan(
                day=5,
                title="处理订单与售后",
                tasks=[
                    "处理第一批订单",
                    "向买家确认收货地址",
                    "在下单平台完成采购",
                ],
            ),
            DayPlan(
                day=6,
                title="数据分析与优化",
                tasks=[
                    "分析哪些品类/价格带更受欢迎",
                    "调整选品策略",
                    "优化商品信息",
                ],
            ),
            DayPlan(
                day=7,
                title="扩大规模",
                tasks=[
                    "根据数据反馈确定稳定货源",
                    "扩展商品种类",
                    "制定日销目标",
                ],
            ),
        ]

    def _generate_video_plan(self, hustle: SideHustle, profile: UserProfile) -> list[DayPlan]:
        """短视频剪辑 7 日计划"""
        return [
            DayPlan(
                day=1,
                title="工具准备与学习",
                tasks=[
                    "安装剪辑软件（剪映专业版/Adobe Premiere）",
                    "学习基础操作（剪辑、调色、音频）",
                    "准备素材来源渠道",
                ],
            ),
            DayPlan(
                day=2,
                title="接单平台入驻",
                tasks=[
                    "在猪八戒/闲鱼/淘宝发布剪辑服务",
                    "制作服务展示页和报价单",
                    "研究竞争对手的定价",
                ],
                templates={
                    "服务介绍": "专业视频剪辑服务，擅长{类型}，交付时间{时间}，修改{次数}次以内免费"
                }
            ),
            DayPlan(
                day=3,
                title="完成第一单",
                tasks=[
                    "接受第一笔订单",
                    "与甲方沟通需求",
                    "完成剪辑并交付",
                ],
            ),
            DayPlan(
                day=4,
                title="建立作品集",
                tasks=[
                    "整理已完成的优秀作品",
                    "制作作品集展示页",
                    "开始在社交媒体展示",
                ],
            ),
            DayPlan(
                day=5,
                title="优化流程",
                tasks=[
                    "分析第一单的时间成本",
                    "建立素材库和模板库",
                    "优化工作流程",
                ],
            ),
            DayPlan(
                day=6,
                title="拓展客户",
                tasks=[
                    "在更多平台发布服务",
                    "尝试主动联系本地商家",
                    "加入剪辑师社群",
                ],
            ),
            DayPlan(
                day=7,
                title="复盘与定价",
                tasks=[
                    "复盘本周收入和时间投入",
                    "调整定价策略",
                    "制定下周目标",
                ],
            ),
        ]

    def _generate_template_plan(self, hustle: SideHustle, profile: UserProfile) -> list[DayPlan]:
        """数字模板销售 7 日计划"""
        return [
            DayPlan(
                day=1,
                title="确定模板类型",
                tasks=[
                    "选择模板方向（PPT/Excel/简历/设计素材）",
                    "研究市场需求和竞品",
                    "确定首批制作数量（建议 3-5 个）",
                ],
            ),
            DayPlan(
                day=2,
                title="制作第一批模板",
                tasks=[
                    "使用工具制作 3-5 个高质量模板",
                    "确保模板可编辑性强",
                    "制作使用说明",
                ],
            ),
            DayPlan(
                day=3,
                title="平台入驻",
                tasks=[
                    "注册小红书/淘宝/闲鱼店铺",
                    "上架模板商品",
                    "设置价格和售后说明",
                ],
                templates={
                    "商品描述": "{模板名称}模板，适用场景：{场景}，包含{内容}，格式：{格式}，支持{软件}编辑"
                }
            ),
            DayPlan(
                day=4,
                title="内容营销",
                tasks=[
                    "在小红书发布模板展示帖",
                    "制作使用效果对比图",
                    "引导私信或店铺下单",
                ],
                templates={
                    "发帖话术": "分享一套我刚制作的{模板类型}，适合{人群}使用！需要的姐妹私信我~"
                }
            ),
            DayPlan(
                day=5,
                title="收集反馈",
                tasks=[
                    "收集第一批用户反馈",
                    "根据反馈优化模板",
                    "更新商品页面",
                ],
            ),
            DayPlan(
                day=6,
                title="扩大SKU",
                tasks=[
                    "开发更多模板类型",
                    "建立模板素材库",
                    "考虑推出会员套餐",
                ],
            ),
            DayPlan(
                day=7,
                title="复盘与迭代",
                tasks=[
                    "分析本周销售数据",
                    "确定爆款方向",
                    "制定下周上新计划",
                ],
            ),
        ]

    def _generate_service_plan(self, hustle: SideHustle, profile: UserProfile) -> list[DayPlan]:
        """本地生活服务 7 日计划"""
        return [
            DayPlan(
                day=1,
                title="服务准备",
                tasks=[
                    "确定服务项目和定价",
                    "准备服务工具和材料",
                    "拍摄服务过程照片",
                ],
            ),
            DayPlan(
                day=2,
                title="平台入驻",
                tasks=[
                    "注册美团/58到家/闲鱼",
                    "完成实名认证",
                    "发布服务信息",
                ],
                templates={
                    "服务介绍": "{服务项目}，{年限}经验，{人数}好评，价格{区间}，服务范围：{区域}"
                }
            ),
            DayPlan(
                day=3,
                title="线下推广",
                tasks=[
                    "在社区张贴服务广告",
                    "加入本地生活服务群",
                    "联系物业或居委会",
                ],
            ),
            DayPlan(
                day=4,
                title="接单服务",
                tasks=[
                    "接收并确认第一笔订单",
                    "按时完成服务",
                    "拍照记录效果",
                ],
            ),
            DayPlan(
                day=5,
                title="积累口碑",
                tasks=[
                    "邀请客户好评",
                    "在社交媒体展示服务案例",
                    "建立老客户优惠机制",
                ],
            ),
            DayPlan(
                day=6,
                title="扩展渠道",
                tasks=[
                    "尝试多个平台",
                    "与相关行业异业合作",
                    "建立转介绍机制",
                ],
            ),
            DayPlan(
                day=7,
                title="复盘优化",
                tasks=[
                    "复盘本周服务情况",
                    "优化服务流程",
                    "调整定价策略",
                ],
            ),
        ]

    def _generate_generic_plan(self, hustle: SideHustle, profile: UserProfile) -> list[DayPlan]:
        """通用 7 日计划"""
        return [
            DayPlan(day=1, title="了解与准备", tasks=["了解项目详情", "准备必要工具", "研究市场"]),
            DayPlan(day=2, title="学习与实践", tasks=["学习核心技能", "完成第一个小任务", "记录问题"]),
            DayPlan(day=3, title="试水与调整", tasks=["尝试接单或发布", "收集反馈", "调整方向"]),
            DayPlan(day=4, title="正式起步", tasks=["建立稳定输出", "开始获客", "处理咨询"]),
            DayPlan(day=5, title="交付与服务", tasks=["完成第一笔交付", "建立客户关系", "获取好评"]),
            DayPlan(day=6, title="扩大规模", tasks=["增加曝光", "优化流程", "考虑扩展"]),
            DayPlan(day=7, title="复盘规划", tasks=["复盘成果", "总结经验", "规划下周"]),
        ]

    def _get_success_metrics(self, hustle: SideHustle) -> list[str]:
        """获取成功指标"""
        return [
            "7 天内完成第一个订单/交易",
            "14 天内建立稳定的获客渠道",
            "30 天内达到设定的月收入目标的 30%",
        ]

    def _get_fallback_options(self, hustle: SideHustle) -> list[str]:
        """获取备选方案"""
        if "内容" in hustle.name or "AI" in hustle.name:
            return ["转向数字模板销售", "尝试自由撰稿", "做剪辑代工"]
        elif "电商" in hustle.name:
            return ["尝试不同平台", "转型数字产品", "做二手闲置"]
        elif "服务" in hustle.name:
            return ["尝试线上服务类副业", "做技能培训"]
        return ["调整目标受众", "选择其他副业方向"]

    def _get_tips(self, hustle: SideHustle) -> list[str]:
        """获取注意事项"""
        tips = [
            "坚持执行，不要因为短期效果不明显就放弃",
            "注重客户反馈，及时调整策略",
            "控制启动成本，避免过度投入",
        ]

        if hustle.startup_cost > 3000:
            tips.append("启动成本较高，建议先从小规模开始")

        if hustle.learning_curve.value == "高级技能":
            tips.append("需要较长的学习周期，建议利用碎片时间持续学习")

        return tips
