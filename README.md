# 副业雷达

> 基于多智能体协同的个性化轻创业推荐系统

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 配置 API Key

支持多种大模型，选择其中一个即可：

```bash
# DeepSeek（默认，推荐）
export DEEPSEEK_API_KEY=your_key_here

# 阿里云千问
export QWEN_API_KEY=your_key_here

# Kimi (Moonshot)
export KIMI_API_KEY=your_key_here

# MiniMax
export MINIMAX_API_KEY=your_key_here

# OpenAI
export OPENAI_API_KEY=your_key_here

# Anthropic (Claude)
export ANTHROPIC_API_KEY=your_key_here
```

或通过环境变量指定 Provider：

```bash
export LLM_PROVIDER=deepseek
export LLM_API_KEY=your_key_here
```

### 3. 启动服务

```bash
# 开发模式
uvicorn side_hustle_agent.main:app --reload --port 8000

# 访问 http://localhost:8000/docs 查看 API 文档
```

### 4. CLI 交互模式

```bash
python -m side_hustle_agent.cli
```

## 支持的模型

| Provider | 环境变量 | 默认模型 |
|----------|----------|----------|
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat |
| 千问(Qwen) | `QWEN_API_KEY` | qwen-turbo |
| Kimi | `KIMI_API_KEY` | moonshot-v1-8k |
| MiniMax | `MINIMAX_API_KEY` | MiniMax-Text-01 |
| OpenAI | `OPENAI_API_KEY` | gpt-4o |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet |

## API 使用

### POST /api/recommend

```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "city": "上海",
    "skills": ["Python", "Excel"],
    "available_time": "每天1-2小时",
    "risk_preference": "稳健型",
    "avoid_appearing": true,
    "monthly_goal": 5000
  }'
```

### POST /api/feedback

```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "city": "上海",
    "skills": ["Python"],
    "available_time": "每天1-2小时",
    "risk_preference": "稳健型",
    "avoid_appearing": true,
    "monthly_goal": 5000,
    "feedback": "failed",
    "reason": "平台注册被拒"
  }'
```

## 项目结构

```
side_hustle_agent/
├── agents/              # 多 Agent 实现
│   ├── base.py         # Agent 基类
│   ├── user_profiler.py
│   ├── opportunity_miner.py
│   ├── action_planner.py
│   └── validator.py
├── core/               # 核心模块
│   ├── models.py      # 数据模型
│   ├── memory.py      # 共享记忆池
│   ├── session.py     # 会话管理
│   └── config.py      # 配置管理
├── knowledge/          # 知识库
│   ├── side_hustles.json   # 副业数据 (20个)
│   └── city_data.py        # 城市数据 (26个城市)
├── llm/                # LLM Provider
│   └── providers.py   # 多模型支持
├── prompts/           # 提示词模板
├── api/               # FastAPI 路由
├── orchestrator.py    # Agent 编排器
├── cli.py             # CLI 工具
└── main.py            # 应用入口
```

## 运行测试

```bash
# 无需 API Key
python tests/test_core.py
```

## 系统架构

```
用户输入 → 用户理解 Agent → 副业匹配 Agent → 执行规划 Agent → 验证 Agent → 推荐结果
```

四个 Agent 协作：
1. **UserProfiler** - 解析用户画像
2. **OpportunityMiner** - 匹配副业知识库
3. **ActionPlanner** - 生成 7 日行动计划
4. **Validator** - 事实核查
