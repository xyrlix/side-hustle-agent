# 开发者指南

本文档为开发人员提供副业雷达系统的开发指导。

---

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/xyrlix/side-hustle-agent.git
cd side-hustle-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -e .
pip install fastapi uvicorn pydantic-settings anthropic
```

### 2. 启动服务

```bash
# 启动前后端（推荐）
python start.py

# 仅后端
uvicorn side_hustle_agent.main:app --reload --port 8000
```

### 3. 访问应用

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 项目结构

### 后端 (side_hustle_agent/)

```
side_hustle_agent/
├── agents/           # AI Agent 实现
├── api/routes.py     # API 路由定义
├── core/             # 核心模块 (数据库、认证、配置)
├── platforms/        # 第三方平台 OAuth
├── data/             # SQLite 数据库
└── main.py          # FastAPI 入口
```

### 前端 (frontend/src/)

```
frontend/src/
├── App.tsx          # 主应用组件
├── api/index.ts    # API 调用封装
└── components/     # React 组件
```

---

## 添加新功能

### 后端 API

1. **在 `routes.py` 中添加路由**

```python
@router.get("/api/new-feature")
async def new_feature_api(request: Request):
    """新功能说明"""
    user = await get_current_user(request)
    if not user:
        return {"success": False, "message": "请先登录"}

    # 业务逻辑
    result = do_something()

    return {"success": True, "data": result}
```

2. **在数据库模块添加 CRUD（如需要）**

```python
# side_hustle_agent/core/database.py

def create_new_entity(user_id: int, **kwargs) -> dict:
    """创建新实体"""
    conn = get_db()
    cursor = conn.cursor()
    # ... 执行插入
    conn.commit()
    conn.close()
    return {"id": new_id, ...}

def get_new_entity(entity_id: int, user_id: int) -> dict | None:
    """获取实体详情"""
    # ...
```

### 前端组件

1. **创建组件文件**

```typescript
// frontend/src/components/NewFeaturePanel.tsx
import { useState } from "react";
import { getToken } from "../api";

interface Props {
  onBack: () => void;
}

export default function NewFeaturePanel({ onBack }: Props) {
  const [loading, setLoading] = useState(false);

  const handleAction = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/new-feature`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      const data = await res.json();
      // 处理结果
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">新功能</h2>
        <button onClick={onBack} className="...">返回</button>
      </div>
      {/* 功能内容 */}
    </div>
  );
}
```

2. **在 App.tsx 中注册路由**

```typescript
// 1. 导入组件
import NewFeaturePanel from "./components/NewFeaturePanel";

// 2. 添加 Page 类型
type Page = "dashboard" | "hustle" | ... | "newfeature";

// 3. 添加导航项
const navItems = [
  // ...
  { id: "newfeature", label: "新功能", icon: "✨" }
];

// 4. 添加路由
{page === "newfeature" && (
  <NewFeaturePanel onBack={() => setPage("dashboard")} />
)}
```

---

## 模块开发指南

### 热点话题模块 (hot_topics.py)

```python
from side_hustle_agent.hot_topics import get_hot_topics_fetcher

# 获取话题
fetcher = get_hot_topics_fetcher()

# 获取微博热搜
weibo_data = await fetcher.fetch_weibo_hot()

# 获取抖音热榜
douyin_data = await fetcher.fetch_douyin_trending()

# 获取所有平台
all_data = await fetcher.fetch_all()
```

### 内容检测模块 (content_filter.py)

```python
from side_hustle_agent.content_filter import check_content, suggest_fix

# 检测内容
result = check_content("这是一段待检测的文本内容")

# 返回结构
# {
#   "passed": bool,           # 是否通过
#   "violations": [            # 违规列表
#     {"type": "ad", "category": "广告违规", "word": "最高级", "position": 0}
#   ],
#   "score": int,              # 质量分 0-100
#   "summary": str             # 检测摘要
# }

# 获取修改建议
if not result["passed"]:
    suggestions = suggest_fix(text, result["violations"])
```

### ROI 分析模块 (roi_analyzer.py)

```python
from side_hustle_agent.roi_analyzer import analyze_content_roi, analyze_campaign_roi

# 分析单内容 ROI
content_data = {
    "views": 10000,
    "likes": 500,
    "comments": 100,
    "shares": 50,
    "revenue": 100.0,
    "platform": "wechat_public"
}
roi = analyze_content_roi(content_data, investment=50)

# 分析整体 ROI
contents = [content_data, ...]
campaign_roi = analyze_campaign_roi(contents, investment=500)
```

### 内容生成 Agent (content_generator.py)

```python
from side_hustle_agent.agents.content_generator import ContentGeneratorAgent, ContentAdaptor
from side_hustle_agent.core.memory import get_memory

# 生成内容
agent = ContentGeneratorAgent(get_memory())
result = await agent.run({
    "topic": "副业赚钱技巧",
    "platform": "wechat_public",
    "style": "专业",
    "length": "中等"
})

# 内容适配
adaptor = ContentAdaptor(agent)
versions = await adaptor.adapt(content_model, ["xiaohongshu", "toutiao"])
```

---

## 数据库操作

### 使用 get_db()

```python
from side_hustle_agent.core.database import get_db

conn = get_db()
cursor = conn.cursor()

# 查询
cursor.execute("SELECT * FROM content WHERE user_id = ?", (user_id,))
rows = cursor.fetchall()

# 插入/更新
cursor.execute("INSERT INTO content (user_id, title) VALUES (?, ?)", (user_id, title))
conn.commit()

# 关闭连接
conn.close()
```

### JSON 字段处理

```python
import json

# 读取 JSON 字段
content = dict(row)
content["tags"] = json.loads(content.get("tags", "[]"))
content["platform_versions"] = json.loads(content.get("platform_versions", "{}"))

# 写入 JSON 字段
tags_json = json.dumps(tags_list, ensure_ascii=False)
cursor.execute("UPDATE content SET tags = ? WHERE id = ?", (tags_json, content_id))
```

---

## 前端 API 调用

### 使用 contentRequest

```typescript
import { contentRequest } from "./api";

async function fetchData() {
  const data = await contentRequest("/api/content");
  if (data.success) {
    console.log(data.contents);
  }
}
```

### 添加新的 API 函数

```typescript
// frontend/src/api/index.ts

export async function getNewFeature(): Promise<any> {
  return contentRequest(`${API_BASE}/api/new-feature`);
}

export async function createNewEntity(data: any): Promise<any> {
  return contentRequest(`${API_BASE}/api/new-entity`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}
```

---

## 测试

### 运行测试

```bash
# 所有测试
pytest tests/ -v

# 仅单元测试
pytest tests/unit/ -v

# 仅集成测试
pytest tests/integration/ -v

# E2E 测试（需要启动服务）
pytest tests/e2e/ -v
```

### 编写测试

```python
# tests/test_new_feature.py
import pytest

def test_new_feature():
    from side_hustle_agent.new_module import new_function

    result = new_function()
    assert result["expected"] == "value"
```

---

## 代码规范

### Python

- 使用类型注解
- 使用 docstring 记录函数说明
- 遵循 PEP 8

### TypeScript/React

- 使用 TypeScript 类型
- 组件使用 `interface Props`
- 使用 TailwindCSS 工具类

### Git 提交

```
feat: 新功能
fix: 修复问题
refactor: 重构
docs: 文档更新
test: 测试
chore: 其他
```

---

> 最后更新：2026-04-30
