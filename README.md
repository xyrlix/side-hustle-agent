# 副业雷达 - 技术文档

> 基于多智能体协同的个性化轻创业推荐系统

## 项目概述

副业雷达是一个利用多 Agent 协同框架为用户提供个性化副业推荐的系统。用户只需输入基本信息，系统即可生成匹配的副业选项和 7 日启动计划。

### 核心价值

- **个性化匹配**：结合用户技能、时间、风险偏好进行精准匹配
- **可执行性强**：生成详细的 7 日行动计划，包含具体任务和模板
- **闭环迭代**：支持用户反馈后动态调整方案
- **政策加成**：结合城市政策提升推荐可行性

## 系统架构

### 三层多 Agent 协同推理框架

```
┌─────────────────────────────────────────────────────────────┐
│                      用户输入                                │
│         (城市、技能、时间、风险偏好、目标)                      │
└─────────────────────┬─────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Layer 1: 用户理解 Agent                      │
│  User Profiler Agent                                         │
│  - 意图解析 + 地域经济数据匹配                               │
│  - 输出：结构化用户画像标签                                  │
└─────────────────────┬─────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Layer 2: 副业知识图谱 Agent                     │
│  Opportunity Miner Agent                                     │
│  - 长链推理判断适配性                                         │
│  - 匹配 200+ 副业知识库                                       │
│  - 输出：Top 3 推荐及匹配理由                                 │
└─────────────────────┬─────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Layer 3: 执行规划 Agent                       │
│  Action Planner Agent                                        │
│  - 生成 7 日启动计划                                          │
│  - 提供 AI 提示词模板和话术模板                               │
│  - 备选方案和成功指标                                         │
└─────────────────────┬─────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Validator Agent                           │
│  - 政策时效性核查                                             │
│  - 收入预期合理性                                            │
│  - 风险提示完整性                                            │
└─────────────────────────────────────────────────────────────┘
```

### Agent 详解

#### 1. User Profiler Agent (用户理解)

**职责**：将用户简表转化为结构化画像

**输入**：
- 城市
- 技能列表
- 可用时间
- 风险偏好
- 露脸偏好
- 月收入目标

**输出**：
- 城市等级（一线/二线/三线/四线及以下）
- 本地时薪参考
- 市场密度分析
- 画像标签列表

**核心逻辑**：
```python
城市等级推断 → 本地时薪估算 → 技能加成计算 → 标签提取
```

#### 2. Opportunity Miner Agent (副业知识图谱)

**职责**：从知识库中匹配最适合的副业

**匹配规则**：
- 时间匹配：副业最低时间要求 ≤ 用户可用时间
- 露脸偏好：厌恶露脸的用户不会匹配需要露脸的副业
- 启动成本：根据风险偏好过滤过高成本的副业
- 城市等级：四线城市过滤需要特定城市资源的副业

**评分维度**：
| 维度 | 权重 | 说明 |
|------|------|------|
| 时间契合度 | 0-0.15 | 时间要求越宽松得分越高 |
| 技能匹配 | 0-0.15 | 能利用已有技能则加分 |
| 收入潜力 | 0-0.1 | 达到目标得分 |
| 稳定性 | 0-0.1 | 保守型用户偏好高稳定性 |
| 政策加成 | 变量 | 城市政策匹配则加分 |
| 露脸偏好 | 0-0.1 | 符合用户偏好则加分 |

#### 3. Action Planner Agent (执行规划)

**职责**：为推荐的副业生成详细的 7 日计划

**计划结构**：
```json
{
  "day_plans": [
    {
      "day": 1,
      "title": "平台注册与定位",
      "tasks": ["注册平台账号", "完善资料", "研究竞品"],
      "ai_prompts": {"账号简介": "..."},
      "templates": {"发布话术": "..."}
    }
  ],
  "success_metrics": ["7天内完成第一单", "14天建立稳定获客渠道"],
  "fallback_options": ["转向数字模板销售", "尝试自由撰稿"],
  "tips": ["坚持执行，不要因为短期效果不明显就放弃"]
}
```

**不同副业类型生成不同计划模板**：
- AI 内容代工
- 无货源电商
- 短视频剪辑
- 数字模板销售
- 本地生活服务

#### 4. Validator Agent (验证)

**职责**：对推荐和计划进行事实核查

**核查维度**：
1. **政策时效性**：检查城市政策是否仍然有效
2. **收入合理性**：收入预期是否在合理范围内
3. **时间可行性**：每日任务量是否合理
4. **平台规则**：是否遗漏重要平台规则
5. **风险完整性**：风险提示是否充分

## 数据模型

### UserInput (用户输入)

```python
{
    "city": str,                    # 所在城市
    "skills": list[str],           # 拥有技能
    "available_time": TimeAvailability,  # 可用时间枚举
    "risk_preference": RiskPreference,  # 风险偏好枚举
    "avoid_appearing": bool,       # 是否厌恶露脸
    "monthly_goal": int            # 月收入目标（元）
}
```

### UserProfile (用户画像)

```python
{
    "city": str,
    "city_tier": CityTier,         # 一线/二线/三线/四线及以下
    "skills": list[str],
    "available_hours_per_day": float,
    "risk_preference": RiskPreference,
    "avoid_appearing": bool,
    "monthly_goal": int,
    "tags": list[str],             # 画像标签
    "hourly_rate_local": float,    # 本地时薪参考
    "market_density": dict[str, float]  # 各类市场密度
}
```

### SideHustle (副业条目)

```python
{
    "id": str,
    "name": str,
    "description": str,
    "startup_cost": int,           # 启动成本（元）
    "learning_curve": SkillLevel,  # 基础/中级/高级
    "platform_rules": list[str],   # 平台规则要点
    "recent_cases": list[dict],    # 近期变现案例
    "policy_risks": list[str],
    "policy_benefits": list[str],
    "min_time_hours": float,       # 最低时间要求
    "requires_appearance": bool,
    "location_requirements": list[str],
    "income_potential": int,        # 月收入潜力上限
    "scalability": int,            # 1-5 可扩展性
    "stability": int               # 1-5 稳定性
}
```

## API 接口

### POST /api/recommend

获取副业推荐

**请求**：
```json
{
    "city": "上海",
    "skills": ["Python", "Excel"],
    "available_time": "每天1-2小时",
    "risk_preference": "稳健型",
    "avoid_appearing": true,
    "monthly_goal": 5000
}
```

**响应**：
```json
{
    "success": true,
    "message": "推荐完成",
    "data": {
        "user_profile": {...},
        "recommendations": [...],
        "selected_recommendation": {...},
        "action_plan": {...},
        "validation_result": {...}
    }
}
```

### POST /api/feedback

提交执行反馈，用于迭代优化

**请求**：
```json
{
    "feedback": "failed",
    "reason": "平台注册被拒"
}
```

**反馈类型**：
- `success`：执行成功，记录经验
- `failed`：执行失败，切换备选方案
- `adjust`：需要调整参数

## 知识库

### 副业数据库 (side_hustles.json)

当前包含 20 个副业类型：

| ID | 名称 | 启动成本 | 学习曲线 | 收入潜力 |
|----|------|----------|----------|----------|
| ai-content-creation | AI 内容代工 | 500 | 基础 | 12000 |
| no-source-ecommerce | 无货源电商 | 1000 | 基础 | 15000 |
| digital-template | 数字模板销售 | 200 | 中级 | 10000 |
| short-video-editing | 短视频剪辑代工 | 1500 | 中级 | 12000 |
| online-tutoring | 在线家教/答疑 | 300 | 中级 | 10000 |
| freelance-writing | 自由撰稿 | 100 | 中级 | 8000 |
| mini-program-development | 小程序开发 | 3000 | 高级 | 30000 |
| ... | ... | ... | ... | ... |

### 城市数据库 (city_data.py)

覆盖 26 个主要城市，包含：
- 城市等级
- 各技能类别时薪参考
- 市场密度分析
- 政策福利信息

## 部署指南

### 环境要求

- Python 3.10+
- Anthropic API Key

### 安装

```bash
# 克隆项目
git clone <repository>
cd side-hustle-agent

# 安装依赖
pip install -e .

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 配置

```bash
# 设置 API Key
export ANTHROPIC_API_KEY=your_key_here

# 或创建 .env 文件
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### 启动服务

```bash
# 开发模式
uvicorn side_hustle_agent.main:app --reload --port 8000

# 生产模式
uvicorn side_hustle_agent.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### CLI 工具

```bash
# 交互模式
python -m side_hustle_agent.cli
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
python tests/test_core.py

# 使用 pytest
pytest tests/ -v
```

### 项目结构

```
side_hustle_agent/
├── agents/                    # Agent 实现
│   ├── base.py               # Agent 基类
│   ├── user_profiler.py      # 用户画像
│   ├── opportunity_miner.py  # 副业匹配
│   ├── action_planner.py     # 执行规划
│   └── validator.py          # 验证
├── core/                     # 核心模块
│   ├── models.py            # 数据模型
│   ├── memory.py            # 共享记忆池
│   ├── session.py           # 会话管理
│   └── config.py            # 配置
├── knowledge/                # 知识库
│   ├── side_hustles.json    # 副业数据
│   ├── side_hustles.py      # 副业数据库
│   └── city_data.py         # 城市数据
├── prompts/                  # 提示词
├── api/                      # API 路由
├── orchestrator.py          # 编排器
└── main.py                   # 入口
```

## 扩展指南

### 添加新的副业类型

编辑 `side_hustle_agent/knowledge/side_hustles.json`：

```json
{
    "id": "new-hustle",
    "name": "新副业名称",
    "description": "...",
    "startup_cost": 1000,
    "learning_curve": "基础技能",
    "platform_rules": [...],
    "recent_cases": [...],
    "policy_risks": [...],
    "policy_benefits": [...],
    "min_time_hours": 2.0,
    "requires_appearance": false,
    "location_requirements": [],
    "income_potential": 8000,
    "scalability": 3,
    "stability": 3
}
```

### 添加城市数据

编辑 `side_hustle_agent/knowledge/city_data.py`，在 `CITY_ECONOMIC_DATA` 字典中添加新城市。

### 自定义 Agent

参考 `agents/base.py` 中的 `BaseAgent` 类：

```python
from side_hustle_agent.agents.base import BaseAgent

class MyAgent(BaseAgent):
    async def run(self, input_data):
        # 实现逻辑
        pass
```

## 常见问题

### Q: 需要 API Key 吗？

A: 是的，需要设置 `ANTHROPIC_API_KEY` 环境变量。如果不设置，某些依赖 LLM 的功能将不可用，但基础匹配逻辑可以正常工作。

### Q: 如何运行测试？

A: 运行 `python tests/test_core.py` 即可，无需 API Key。

### Q: 支持哪些城市？

A: 目前支持 26 个主要城市，详见 `city_data.py`。

## License

MIT License