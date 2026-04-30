"""
Pytest 配置和公共 fixtures
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_db_path():
    """测试数据库路径"""
    return str(project_root / "data" / "test_side_hustle.db")


@pytest.fixture(scope="function")
def test_db(test_db_path):
    """每个测试使用临时数据库"""
    # 初始化测试数据库
    from side_hustle_agent.core.database import init_db, get_db

    # 确保数据目录存在
    os.makedirs(os.path.dirname(test_db_path), exist_ok=True)

    # 设置测试数据库路径
    os.environ["TEST_DB_PATH"] = test_db_path

    # 初始化数据库
    init_db()

    yield test_db_path

    # 清理
    try:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    except Exception:
        pass


@pytest.fixture
def auth_token():
    """生成测试用 auth token"""
    from side_hustle_agent.core.database import create_token
    token = create_token(user_id=1, username="test_user", role="user")
    return token


@pytest.fixture
def admin_token():
    """生成测试用 admin token"""
    from side_hustle_agent.core.database import create_token
    token = create_token(user_id=1, username="admin", role="admin")
    return token


@pytest.fixture
def test_user(test_db):
    """创建测试用户"""
    from side_hustle_agent.core.database import create_user, get_user_by_username

    # 检查是否已存在
    user = get_user_by_username("test_user")
    if user:
        return user

    # 创建新用户
    result = create_user("test_user", "test_password", "test@example.com")
    return result


@pytest.fixture
def test_client(test_db):
    """创建 FastAPI 测试客户端"""
    from fastapi.testclient import TestClient
    from side_hustle_agent.main import app

    return TestClient(app)


@pytest.fixture
def sample_content_data():
    """示例内容数据"""
    return {
        "title": "测试内容标题",
        "body": "这是测试内容的正文部分，包含一些测试文字。",
        "summary": "这是摘要部分",
        "tags": ["测试", "示例"],
        "category": "测试分类",
    }


@pytest.fixture
def sample_user_input():
    """示例用户输入"""
    from side_hustle_agent.core.models import UserInput, TimeAvailability, RiskPreference, EmploymentStatus, WorkExperience, SideHustleExp, StartupBudget, WorkMode

    return UserInput(
        city="上海",
        skills=["Python", "Excel"],
        available_time=TimeAvailability.ONE_TO_2H,
        risk_preference=RiskPreference.MEDIUM,
        avoid_appearing=True,
        monthly_goal=5000,
        employment_status=EmploymentStatus.EMPLOYED,
        industry="互联网",
        work_experience=WorkExperience.ONE_TO_3Y,
        side_hustle_exp=SideHustleExp.NONE,
        startup_budget=StartupBudget.FIVE_HUNDRED_TO_2K,
        work_mode=WorkMode.ONLINE,
    )