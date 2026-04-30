# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

side-hustle-agent (副业雷达) — 基于多智能体协同的个性化轻创业推荐系统

三层多 Agent 协同推理框架：
1. **用户理解 Agent (UserProfiler)** — 解析用户画像标签
2. **副业知识图谱 Agent (OpportunityMiner)** — 匹配 20 个副业知识库
3. **执行规划 Agent (ActionPlanner)** — 生成 7 日启动计划
4. **验证 Agent (Validator)** — 事实核查

## Commands

### 安装依赖
```bash
pip install -e .
pip install fastapi uvicorn pydantic-settings anthropic
```

### 开发
```bash
# 启动服务
python start.py

# 运行测试
pytest tests/unit/ tests/integration/ -v

# E2E 测试（需要服务运行）
pytest tests/e2e/ -v
```

### 环境变量
```bash
export ANTHROPIC_API_KEY=your_key_here  # 或设置 SIDE_HUSTLE_ANTHROPIC_API_KEY
```

## Architecture

```
side_hustle_agent/
├── agents/                    # 多 Agent 实现
│   ├── base.py               # Agent 基类
│   ├── user_profiler.py      # 用户画像 Agent
│   ├── opportunity_miner.py  # 副业匹配 Agent
│   ├── action_planner.py      # 执行规划 Agent（生成 7 日计划）
│   └── validator.py          # 验证 Agent
├── core/                     # 核心模块
│   ├── models.py            # Pydantic 数据模型
│   ├── memory.py            # 共享记忆池
│   ├── session.py           # 会话管理
│   └── logging.py           # 日志配置
├── knowledge/               # 知识库
│   ├── side_hustles.json    # 20 个副业条目
│   ├── side_hustles.py      # 副业数据库
│   └── city_data.py         # 城市经济数据（26 个城市）
├── prompts/                  # 提示词模板
├── api/                      # FastAPI 路由
│   └── routes.py            # /api/recommend, /api/feedback
├── orchestrator.py          # Agent 编排器
├── cli.py                   # CLI 工具
└── main.py                  # FastAPI 应用入口
```

## API

### POST /api/recommend
获取副业推荐

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

### POST /api/feedback
提交执行反馈（迭代优化）

```json
{
    "feedback": "failed",
    "reason": "平台注册被拒"
}
```

## 数据模型

- `UserInput` — 用户输入
- `UserProfile` — 用户画像
- `SideHustle` — 副业条目
- `Recommendation` — 推荐结果
- `ActionPlan` — 7 日行动计划
- `ValidationResult` — 验证结果