# 副业雷达 - 系统架构文档

本文档详细描述副业雷达系统的技术架构、模块设计和代码流程。

---

## 目录

- [系统概述](#系统概述)
- [技术架构](#技术架构)
- [前端架构](#前端架构)
- [后端架构](#后端架构)
- [数据模型](#数据模型)
- [核心模块](#核心模块)
- [工作流设计](#工作流设计)
- [API 接口](#api-接口)

---

## 系统概述

副业雷达是一个基于多智能体协同的个性化轻创业推荐系统，同时具备多平台社交媒体内容管理能力。

### 核心功能

1. **副业推荐** - AI 智能分析用户画像，匹配最适合的副业方向
2. **内容管理** - 创建、编辑、发布多平台内容
3. **平台管理** - 管理多个社交媒体平台账号
4. **数据分析** - 内容运营数据统计和分析
5. **热点追踪** - 获取各平台热点话题
6. **内容检测** - 违规词检测和修改建议
7. **ROI 分析** - 内容投资回报率分析

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (React + TypeScript)                  │
│         侧边栏导航 / 工作流页面 / 组件化设计 / TailwindCSS         │
└─────────────────────────────────────────────────────────────────┘
                                  │ HTTP/REST
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API 网关层 (FastAPI)                         │
│              认证中间件 / 权限控制 / 限流 / 日志                   │
└─────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│   用户权限模块  │        │  内容创作模块  │        │  平台管理模块  │
│   RBAC + JWT  │        │  AI 生成     │        │  OAuth 2.0   │
└───────────────┘        └───────────────┘        └───────────────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       数据层 (SQLite)                            │
│     users / content / campaigns / platforms / analytics            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 前端架构

### 技术栈

- **框架**: React 18 + TypeScript
- **样式**: TailwindCSS (深色主题)
- **构建**: Vite
- **状态管理**: React Hooks (useState/useEffect)

### 项目结构

```
frontend/src/
├── App.tsx                    # 主应用入口
├── api/
│   └── index.ts               # API 调用封装
├── components/
│   ├── ContentManager.tsx     # 内容管理
│   ├── AnalyticsDashboard.tsx  # 数据分析
│   ├── PlatformManager.tsx    # 平台管理
│   ├── MaterialManager.tsx     # 素材库
│   ├── ScheduledPostsManager.tsx  # 定时发布
│   ├── HotTopicsPanel.tsx     # 热点话题
│   ├── ContentCheckPanel.tsx   # 内容检测
│   ├── ROIAnalysisPanel.tsx   # ROI分析
│   ├── AdminPanel.tsx         # 管理面板
│   ├── LoginModal.tsx         # 登录弹窗
│   ├── HeroBackground.tsx     # 背景组件
│   └── ...
└── index.css                  # 全局样式
```

### 布局设计

采用侧边栏导航布局，按工作流分组：

```
┌─────────┬──────────────────────────────────────────┐
│         │  面包屑导航                               │
│  侧边栏  ├──────────────────────────────────────────┤
│  可折叠  │                                          │
│         │           主内容区域                        │
│ 工作台   │                                          │
│ 副业分析 │                                          │
│ 内容创作 │                                          │
│ 发布管理 │                                          │
│ 数据分析 │                                          │
└─────────┴──────────────────────────────────────────┘
```

**工作流分组**:
- **工作台**: 首页仪表板
- **副业分析**: 副业推荐
- **内容创作**: 内容管理 / 素材库 / 热点话题 / 内容检测
- **发布管理**: 平台管理 / 定时发布
- **数据分析**: 数据分析 / ROI分析

### 组件设计模式

```typescript
// 组件 Props 接口
interface Props {
  token?: string;      // 认证 token
  onBack: () => void;  // 返回回调
}

// 使用示例
export default function ContentManager({ token, onBack }: Props) {
  // ...
}
```

---

## 后端架构

### 技术栈

- **框架**: FastAPI
- **数据库**: SQLite
- **ORM**: 原生 SQL (sqlite3)
- **认证**: JWT Token

### 项目结构

```
side_hustle_agent/
├── agents/                        # AI Agent 模块
│   ├── base.py                   # Agent 基类
│   ├── user_profiler.py          # 用户画像 Agent
│   ├── opportunity_miner.py      # 副业匹配 Agent
│   ├── action_planner.py         # 执行规划 Agent
│   ├── validator.py              # 验证 Agent
│   └── content_generator.py       # 内容生成 Agent
├── core/                         # 核心模块
│   ├── models.py                # Pydantic 数据模型
│   ├── database.py              # 数据库 CRUD
│   ├── auth.py                  # 认证和权限
│   ├── config.py                # 配置管理
│   └── memory.py                # 共享记忆
├── platforms/                    # 平台集成
│   ├── base.py                  # PlatformOAuth 基类
│   ├── wechat.py                # 微信公众号
│   ├── toutiao.py               # 头条号
│   └── xiaohongshu.py           # 小红书
├── api/
│   └── routes.py                # API 路由
├── hot_topics.py                 # 热点话题获取
├── content_filter.py             # 内容违规检测
├── roi_analyzer.py               # ROI 分析
├── mmx_client.py               # 本地 AI 客户端
└── main.py                      # FastAPI 入口
```

---

## 数据模型

### 用户相关

```python
# 用户表
users (
    id: INTEGER PRIMARY KEY
    username: TEXT UNIQUE
    password_hash: TEXT
    email: TEXT
    role: TEXT DEFAULT 'user'  # admin/owner/editor/viewer
    created_at: TIMESTAMP
    last_login: TIMESTAMP
)

# RBAC 表
roles (id, name, description)
permissions (id, name, resource, action)
role_permissions (role_id, permission_id)
user_roles (user_id, role_id, scope)
```

### 内容相关

```python
# 内容表
content (
    id: INTEGER PRIMARY KEY
    user_id: INTEGER
    title: TEXT
    body: TEXT
    summary: TEXT
    cover_image: TEXT
    platform_versions: TEXT  # JSON 各平台适配版本
    material_ids: TEXT        # JSON 素材ID列表
    status: TEXT             # draft/pending/published/failed
    tags: TEXT               # JSON
    category: TEXT
    scheduled_at: TIMESTAMP
    published_at: TIMESTAMP
    published_platforms: TEXT  # JSON
    ai_generated: BOOLEAN
    ai_prompt: TEXT
    views: INTEGER
    likes: INTEGER
    comments: INTEGER
    shares: INTEGER
    revenue: REAL
    version: INTEGER
    created_at: TIMESTAMP
    updated_at: TIMESTAMP
)

# 内容版本历史
content_versions (
    id, content_id, version, title, body, change_summary, created_at
)

# 运营活动
campaigns (
    id, user_id, name, description, content_ids, start_date, end_date,
    target_views, target_revenue, actual_views, actual_revenue, status, created_at
)
```

### 平台相关

```python
# 平台账号
platform_accounts (
    id, user_id, platform, account_name, account_id,
    access_token, refresh_token, status, followers, created_at, updated_at
)

# 素材
materials (
    id, user_id, filename, file_path, file_type, file_size, mime_type,
    width, height, duration, tags, folder, created_at
)

# 发布日志
publish_logs (
    id, content_id, platform, status, error_message, published_url, published_at, created_at
)
```

### 数据分析

```python
# 定时发布任务
scheduled_posts (
    id, content_id, platform, scheduled_at, status, created_at
)

# 分析数据
analytics (
    id, user_id, platform, date,
    views, likes, comments, shares, followers, revenue
)
```

---

## 核心模块

### 1. 用户画像 Agent (UserProfiler)

**职责**: 解析用户输入，生成结构化用户画像

**输入**:
```python
UserInput(
    city="上海",
    skills=["Python", "Excel"],
    available_time="每天1-2小时",
    risk_preference="稳健型",
    avoid_appearing=True,
    monthly_goal=5000,
    employment_status="在职",
    industry="互联网",
    work_experience="1-3年",
    side_hustle_exp="有一些",
    startup_budget="500-2000元",
    work_mode="线上为主"
)
```

**输出**:
```python
UserProfile(
    city="上海",
    city_tier="一线城市",
    skills=["Python", "Excel"],
    available_hours_per_day=1.5,
    risk_preference="稳健型",
    avoid_appearing=True,
    monthly_goal=5000,
    tags=["互联网从业者", "有副业经验", ...],
    # ... 更多画像标签
)
```

### 2. 副业匹配 Agent (OpportunityMiner)

**职责**: 从20个副业知识库中匹配最适合的副业

**知识库条目结构**:
```python
SideHustle(
    id="freelance_writer",
    name="自由攥稿人",
    description="...",
    startup_cost=0,
    learning_curve="基础技能",
    income_potential=8000,
    scalability=4,
    stability=2,
    min_time_hours=2,
    requires_appearance=False,
    # ... 更多属性
)
```

### 3. 执行规划 Agent (ActionPlanner)

**职责**: 生成7日启动计划

**输出**:
```python
ActionPlan(
    side_hustle=SideHustle(...),
    day_plans=[
        DayPlan(day=1, title="账号搭建", tasks=[...]),
        DayPlan(day=2, title="内容规划", tasks=[...]),
        # ...
    ],
    success_metrics=["粉丝数", "阅读量"],
    fallback_options=[...],
    tips=[...]
)
```

### 4. 内容生成 Agent (ContentGeneratorAgent)

**职责**: AI 生成各平台适配内容

**平台提示词模板**:
```python
PLATFORM_PROMPTS = {
    "wechat_public": """你是一位资深公众号编辑，擅长撰写深度文章。
    要求：
    - 标题吸引人且有传播性
    - 文章结构：开篇引入 + 3-5个核心观点 + 总结升华
    - 语言风格：专业但不晦涩，善用讲故事的方式
    - 字数要求：1500-3000字""",

    "xiaohongshu": """你是一位小红书博主，擅长撰写种草笔记。
    要求：
    - 标题要有情绪感和代入感，善用emoji
    - 正文字数精简，每段不超过3行
    - 善用标签和话题增加曝光
    - 字数要求：500-1000字""",
    # ...
}
```

### 5. 热点话题模块 (HotTopicsFetcher)

**职责**: 获取各平台热点话题

```python
class HotTopicsFetcher:
    async def fetch_weibo_hot(self) -> dict  # 微博热搜
    async def fetch_douyin_trending(self) -> dict  # 抖音热榜
    async def fetch_toutiao_hot(self) -> dict  # 头条热榜
    async def fetch_all(self) -> dict  # 并发获取所有
```

### 6. 内容检测模块 (ContentFilter)

**职责**: 检测违规词和限流风险

```python
class ContentFilter:
    def check(self, text: str) -> dict:
        # 返回: {passed, violations, score, summary}
        # violations: [{type, category, word, position}]

    def suggest_fix(self, text: str, violations: list) -> dict:
        # 返回修改建议
```

**违规类型**:
- `ad`: 广告违规（最高级、绝对化用语）
- `limit`: 平台限流词（微信/抖音等平台敏感词）
- `quality`: 内容重复

### 7. ROI 分析模块 (ROIAnalyzer)

**职责**: 计算内容投资回报率

```python
class ROIAnalyzer:
    def analyze_content_roi(self, content_data: dict, investment: float) -> dict:
        # 返回: {views, likes, comments, shares, revenue, roi, cpm, engagement_rate, rating}

    def analyze_campaign_roi(self, contents: list, investment: float) -> dict:
        # 返回整体 ROI 分析

    def get_investment_advice(self, current_roi: float, target_roi: float) -> dict:
        # 返回优化建议
```

---

## 工作流设计

### 副业推荐流程

```
用户输入 → 用户画像 Agent → 副业匹配 Agent → 执行规划 Agent → 验证 Agent → 推荐结果
```

### 内容创作流程

```
选题 → AI生成内容 → 内容检测 → 编辑优化 → 多平台适配 → 发布/定时发布
```

### 发布管理流程

```
内容创建 → 平台适配 → 定时发布队列 → 调度器执行 → 发布日志记录
```

---

## API 接口

### 认证相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/auth/me | 获取当前用户 |

### 副业推荐

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/recommend | 获取副业推荐 |
| POST | /api/feedback | 提交执行反馈 |

### 内容管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/content | 创建内容 |
| GET | /api/content | 列表内容 |
| GET | /api/content/{id} | 内容详情 |
| PUT | /api/content/{id} | 更新内容 |
| DELETE | /api/content/{id} | 删除内容 |
| GET | /api/content/{id}/versions | 版本历史 |
| POST | /api/content/{id}/publish | 发布内容 |

### 热点追踪

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/hot-topics | 获取热点话题 |
| GET | /api/hot-topics/sources | 获取支持的来源 |

### 内容检测

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/content/check | 检测内容违规词 |

### ROI 分析

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/roi/content/{id} | 单内容 ROI |
| GET | /api/roi/campaign | 整体 ROI |
| GET | /api/roi/advice | ROI 优化建议 |

### 平台管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/platforms/accounts | 创建平台账号 |
| GET | /api/platforms/accounts | 列表平台账号 |
| PUT | /api/platforms/accounts/{id} | 更新平台账号 |
| DELETE | /api/platforms/accounts/{id} | 删除平台账号 |
| GET | /api/oauth/{platform}/authorize | 获取授权 URL |
| POST | /api/oauth/{platform}/callback | OAuth 回调 |

### 数据分析

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/analytics | 录入数据 |
| GET | /api/analytics | 获取数据列表 |
| GET | /api/analytics/summary | 数据汇总 |

### 定时发布

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/scheduled-posts | 创建定时任务 |
| GET | /api/scheduled-posts | 列表定时任务 |
| DELETE | /api/scheduled-posts/{id} | 取消任务 |

### 素材管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/materials/upload | 上传素材 |
| GET | /api/materials | 列表素材 |
| DELETE | /api/materials/{id} | 删除素材 |

---

## 数据库

SQLite 数据库位于 `side_hustle_agent/data/side_hustle.db`

**默认管理员账户**:
- 用户名: `admin`
- 密码: `admin123`

---

## 环境变量

```bash
# LLM 配置
LLM_PROVIDER=deepseek
LLM_API_KEY=your_api_key
LLM_MODEL=deepseek-chat

# 数据库
DB_PATH=side_hustle_agent/data/side_hustle.db

# 服务器
PORT=8000

# JWT
JWT_SECRET=your_jwt_secret_key
```

---

> 最后更新：2026-04-30
