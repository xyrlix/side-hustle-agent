# 测试框架

## 目录结构

```
tests/
├── conftest.py              # pytest 全局配置和公共 fixtures
├── unit/                    # 单元测试
│   ├── test_models.py       # 数据模型测试
│   ├── test_database.py     # 数据库 CRUD 测试
│   └── test_api.py          # API 端点测试
├── integration/             # 集成测试
│   ├── test_content_flow.py # 内容创作到发布流程
│   └── test_auth_flow.py    # 认证到内容管理流程
└── e2e/                     # 端到端测试
    ├── conftest.py          # Playwright 配置
    └── test_auth_flow.py    # 浏览器端到端测试
```

## 运行测试

### 前置条件

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 可选：集成测试和 E2E 测试需要额外依赖
pip install requests
pip install playwright
playwright install chromium
```

### 运行所有单元测试

```bash
pytest tests/unit/ -v
```

### 运行所有集成测试

```bash
pytest tests/integration/ -v
```

### 运行 E2E 测试（需要服务运行）

```bash
# 1. 启动服务
python start.py

# 2. 运行 E2E 测试
pytest tests/e2e/ -v
```

### 运行所有测试

```bash
pytest tests/ -v
```

## 测试标记

- `unit` - 单元测试，测试独立模块
- `integration` - 集成测试，测试模块间交互
- `e2e` - 端到端测试，需要浏览器环境

## Fixtures

| Fixture | 说明 |
|---------|------|
| `test_db_path` | 测试数据库路径 |
| `test_db` | 每个测试的临时数据库 |
| `test_user` | 测试用户 |
| `test_client` | FastAPI 测试客户端 |
| `auth_token` | 普通用户 Token |
| `admin_token` | 管理员 Token |
| `sample_user_input` | 示例用户输入 |
| `sample_content_data` | 示例内容数据 |

## 编写新测试

### 单元测试

```python
def test_my_feature(test_db):
    """测试独立功能"""
    from side_hustle_agent.core.database import some_function
    result = some_function()
    assert result == expected
```

### 集成测试

```python
def test_feature_flow(test_client, auth_token):
    """测试功能流程"""
    response = test_client.post(
        "/api/endpoint",
        json={"data": "value"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json().get("success") == True
```

### E2E 测试

```python
def test_browser_flow(page: Page):
    """测试浏览器交互"""
    page.goto("http://localhost:1420")
    page.get_by_button("Button").click()
    assert page.get_by_text("Expected").is_visible()
```
