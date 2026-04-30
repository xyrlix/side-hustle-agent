# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

side-hustle-agent (副业雷达) — 基于多智能体协同的个性化轻创业推荐系统 + 多平台社交媒体内容管理系统

### 核心能力

1. **副业推荐** - 多 Agent 协同推理，生成个性化副业建议和 7 日执行计划
2. **内容管理** - 多平台内容创作、编辑、版本管理
3. **平台接入** - 微信公众号、头条号、小红书等 OAuth 接入
4. **热点追踪** - 微博热搜、抖音热榜、头条热榜
5. **内容检测** - 违规词检测、广告词检测、限流风险提醒
6. **ROI 分析** - 内容投资回报率计算和分析

## Commands

### 安装依赖
```bash
pip install -e .
pip install fastapi uvicorn pydantic-settings anthropic
```

### 开发
```bash
# 启动前后端服务
python start.py

# 仅启动后端
uvicorn side_hustle_agent.main:app --reload --port 8000

# 运行测试
pytest tests/unit/ tests/integration/ -v

# E2E 测试（需要服务运行）
pytest tests/e2e/ -v
```

### 环境变量
```bash
export ANTHROPIC_API_KEY=your_key_here
export LLM_PROVIDER=deepseek  # deepseek/anthropic/qwen/kimi/minimax
export LLM_MODEL=deepseek-chat
```

## Architecture

```
side_hustle_agent/
├── agents/                    # AI Agent 模块
│   ├── base.py              # Agent 基类
│   ├── user_profiler.py     # 用户画像 Agent
│   ├── opportunity_miner.py  # 副业匹配 Agent
│   ├── action_planner.py     # 执行规划 Agent
│   ├── validator.py          # 验证 Agent
│   └── content_generator.py  # 内容生成 Agent
├── core/                     # 核心模块
│   ├── models.py            # Pydantic 数据模型
│   ├── database.py          # SQLite CRUD
│   ├── auth.py              # 认证 + RBAC
│   ├── config.py            # 配置管理
│   └── memory.py            # 共享记忆
├── platforms/                # 平台 OAuth
│   ├── base.py              # PlatformOAuth 基类
│   ├── wechat.py            # 微信公众号
│   ├── toutiao.py           # 头条号
│   └── xiaohongshu.py       # 小红书
├── api/
│   └── routes.py            # FastAPI 路由
├── hot_topics.py            # 热点话题获取
├── content_filter.py        # 内容违规检测
├── roi_analyzer.py           # ROI 分析
├── scheduler.py             # 定时任务调度器
├── mmx_client.py            # 本地 AI 客户端
└── main.py                  # FastAPI 入口
```

## Frontend Structure

```
frontend/src/
├── App.tsx                    # 主应用（侧边栏布局）
├── api/
│   └── index.ts               # API 调用封装
└── components/
    ├── ContentManager.tsx     # 内容管理
    ├── AnalyticsDashboard.tsx # 数据分析
    ├── PlatformManager.tsx    # 平台管理
    ├── MaterialManager.tsx     # 素材库
    ├── ScheduledPostsManager.tsx  # 定时发布
    ├── HotTopicsPanel.tsx     # 热点话题
    ├── ContentCheckPanel.tsx  # 内容检测
    ├── ROIAnalysisPanel.tsx   # ROI 分析
    └── ...
```

## 工作流分组

侧边栏按工作流分组：
- **工作台**: 首页仪表板
- **副业分析**: 副业推荐
- **内容创作**: 内容管理 / 素材库 / 热点话题 / 内容检测
- **发布管理**: 平台管理 / 定时发布
- **数据分析**: 数据分析 / ROI 分析

## API 核心端点

### 副业推荐
- `POST /api/recommend` - 获取推荐
- `POST /api/feedback` - 提交反馈

### 内容管理
- `POST /api/content` - 创建内容
- `GET /api/content` - 列表
- `PUT /api/content/{id}` - 更新
- `DELETE /api/content/{id}` - 删除
- `POST /api/content/{id}/publish` - 发布
- `POST /api/content/check` - 违规检测

### 热点 & ROI
- `GET /api/hot-topics` - 热点话题
- `GET /api/roi/content/{id}` - 单内容 ROI
- `GET /api/roi/campaign` - 整体 ROI

### 平台 & 发布
- `GET /api/platforms` - 平台列表
- `POST /api/platforms/accounts` - 连接平台
- `GET /api/scheduled-posts` - 定时任务
- `POST /api/scheduled-posts` - 创建定时任务

## 数据模型

- `UserInput` — 用户输入
- `UserProfile` — 用户画像
- `SideHustle` — 副业条目
- `Recommendation` — 推荐结果
- `ActionPlan` — 7 日行动计划
- `Content` — 内容条目
- `PlatformAccount` — 平台账号
- `Campaign` — 运营活动
- `Material` — 素材
- `Analytics` — 分析数据

## RBAC 角色

| 角色 | 权限 |
|------|------|
| admin | 所有权限 |
| owner | 内容/平台/分析/素材管理 |
| editor | 创建内容、发布、管理素材 |
| viewer | 只读 |

## 数据库

SQLite: `side_hustle_agent/data/side_hustle.db`
默认管理员: `admin` / `admin123`

## 测试

```bash
# 单元测试 + 集成测试
pytest tests/unit/ tests/integration/ -v

# E2E 测试
pytest tests/e2e/ -v
```
