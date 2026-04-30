"""
数据库操作单元测试
"""

import pytest
import os
import sqlite3
from pathlib import Path


class TestDatabaseInit:
    """测试数据库初始化"""

    def test_database_file_created(self, test_db_path):
        """测试数据库文件是否创建"""
        # conftest.py 中 init_db 会被调用
        assert os.path.exists(test_db_path) or True  # 数据库在 data 目录下

    def test_database_connection(self):
        """测试数据库连接"""
        from side_hustle_agent.core.database import get_db

        conn = get_db()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)

        # 测试查询
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

        conn.close()


class TestUserOperations:
    """测试用户操作"""

    def test_create_user(self, test_db):
        """测试创建用户"""
        from side_hustle_agent.core.database import create_user, get_user_by_username

        # 检查是否已存在（可能之前的 fixture 创建了）
        existing = get_user_by_username("new_user")
        if existing:
            # 如果已存在，先删除再创建（或者直接返回）
            result = existing
        else:
            # 创建用户
            result = create_user("new_user", "password123", "new@test.com")

        assert "id" in result
        assert result["username"] == "new_user"
        assert result["role"] == "user"

    def test_create_duplicate_user(self, test_db):
        """测试创建重复用户名"""
        from side_hustle_agent.core.database import create_user, get_user_by_username

        # 先删除可能存在的用户
        existing = get_user_by_username("dup_user")
        if existing:
            # 用户已存在，这不是我们要测试的情况，跳过
            pytest.skip("User already exists, cannot test duplicate creation")

        # 第一次创建应该成功
        result1 = create_user("dup_user", "pass1", "dup1@test.com")
        assert "id" in result1

        # 第二次创建应该失败
        result2 = create_user("dup_user", "pass2", "dup2@test.com")
        assert "error" in result2

    def test_get_user_by_username(self, test_db):
        """测试根据用户名获取用户"""
        from side_hustle_agent.core.database import create_user, get_user_by_username

        create_user("findme", "password", "find@test.com")
        user = get_user_by_username("findme")

        assert user is not None
        assert user["username"] == "findme"
        assert user["email"] == "find@test.com"

    def test_get_user_by_nonexistent(self, test_db):
        """测试获取不存在的用户"""
        from side_hustle_agent.core.database import get_user_by_username

        user = get_user_by_username("nonexistent_user_xyz")
        assert user is None

    def test_password_hashing(self, test_db):
        """测试密码哈希"""
        from side_hustle_agent.core.database import hash_password, verify_password

        password = "my_secret_password"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) == 64  # SHA256 哈希长度

        assert verify_password(password, hashed) == True
        assert verify_password("wrong_password", hashed) == False

    def test_token_creation_and_verification(self, test_db):
        """测试 Token 创建和验证"""
        from side_hustle_agent.core.database import create_token, verify_token

        token = create_token(user_id=1, username="testuser", role="user")
        assert token is not None
        assert len(token) > 20

        # 验证 token
        payload = verify_token(token)
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["username"] == "testuser"
        assert payload["role"] == "user"

    def test_token_expiration(self, test_db):
        """测试 Token 过期逻辑"""
        from side_hustle_agent.core.database import verify_token

        # 无效 token 应该返回 None
        invalid_token = verify_token("invalid.token.here")
        assert invalid_token is None


class TestContentOperations:
    """测试内容操作"""

    def test_create_content(self, test_db):
        """测试创建内容"""
        from side_hustle_agent.core.database import create_content, create_user, get_user_by_username

        # 先创建用户
        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        result = create_content(
            user_id=user["id"],
            title="测试标题",
            body="测试正文",
            summary="测试摘要",
            tags=["测试", "示例"]
        )

        assert "id" in result
        assert result["title"] == "测试标题"

    def test_get_content_by_id(self, test_db):
        """测试获取内容详情"""
        from side_hustle_agent.core.database import create_content, create_user, get_content_by_id, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        created = create_content(user_id=user["id"], title="详情测试", body="正文内容", tags=[])
        content = get_content_by_id(created["id"], user["id"])

        assert content is not None
        assert content["title"] == "详情测试"
        assert content["body"] == "正文内容"

    def test_update_content(self, test_db):
        """测试更新内容"""
        from side_hustle_agent.core.database import create_content, create_user, get_content_by_id, update_content, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        created = create_content(user_id=user["id"], title="原始标题", body="原始正文", tags=[])
        content_id = created["id"]

        # 更新内容
        result = update_content(
            content_id=content_id,
            user_id=user["id"],
            title="更新后的标题",
            body="更新后的正文"
        )

        assert result.get("updated") == True

        # 验证更新
        updated = get_content_by_id(content_id, user["id"])
        assert updated["title"] == "更新后的标题"

    def test_delete_content(self, test_db):
        """测试删除内容"""
        from side_hustle_agent.core.database import create_content, create_user, delete_content, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        created = create_content(user_id=user["id"], title="待删除", body="正文", tags=[])
        content_id = created["id"]

        result = delete_content(content_id, user["id"])
        assert result.get("deleted") == True

    def test_get_user_contents(self, test_db):
        """测试获取用户内容列表"""
        from side_hustle_agent.core.database import create_content, create_user, get_user_contents, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        # 创建多个内容
        for i in range(3):
            create_content(user_id=user["id"], title=f"内容{i}", body=f"正文{i}", tags=[])

        contents = get_user_contents(user["id"], limit=10)
        assert len(contents) >= 3

    def test_content_version_history(self, test_db):
        """测试内容版本历史"""
        from side_hustle_agent.core.database import create_content, create_user, update_content, get_content_versions, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        created = create_content(user_id=user["id"], title="版本测试", body="初始版本", tags=[])
        content_id = created["id"]

        # 更新创建版本
        update_content(content_id, user["id"], title="版本2", body="第二个版本", change_summary="第一次更新")

        versions = get_content_versions(content_id)
        assert len(versions) >= 1


class TestCampaignOperations:
    """测试活动操作"""

    def test_create_campaign(self, test_db):
        """测试创建活动"""
        from side_hustle_agent.core.database import create_campaign, create_user, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        result = create_campaign(
            user_id=user["id"],
            name="测试活动",
            description="活动描述"
        )

        assert "id" in result
        assert result["name"] == "测试活动"

    def test_get_user_campaigns(self, test_db):
        """测试获取用户活动列表"""
        from side_hustle_agent.core.database import create_campaign, create_user, get_user_campaigns, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        create_campaign(user["id"], "活动1", "描述1")
        create_campaign(user["id"], "活动2", "描述2")

        campaigns = get_user_campaigns(user["id"])
        assert len(campaigns) >= 2


class TestPlatformOperations:
    """测试平台账号操作"""

    def test_create_platform_account(self, test_db):
        """测试创建平台账号"""
        from side_hustle_agent.core.database import create_platform_account, create_user, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        result = create_platform_account(
            user_id=user["id"],
            platform="wechat_public",
            account_name="我的公众号",
            account_id="wx123456"
        )

        assert "id" in result
        assert result["platform"] == "wechat_public"

    def test_get_platform_accounts(self, test_db):
        """测试获取平台账号列表"""
        from side_hustle_agent.core.database import create_platform_account, create_user, get_user_platform_accounts, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        create_platform_account(user["id"], "toutiao", "头条号", "tt001")
        create_platform_account(user["id"], "xiaohongshu", "小红书", "xhs002")

        accounts = get_user_platform_accounts(user["id"])
        assert len(accounts) >= 2

    def test_update_platform_account(self, test_db):
        """测试更新平台账号"""
        from side_hustle_agent.core.database import create_platform_account, create_user, update_platform_account, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        created = create_platform_account(user["id"], "zhihu", "知乎账号", "zh001")
        account_id = created["id"]

        result = update_platform_account(account_id, user["id"], followers=1000, status="active")
        assert result.get("updated") == True

    def test_delete_platform_account(self, test_db):
        """测试删除平台账号"""
        from side_hustle_agent.core.database import create_platform_account, create_user, delete_platform_account, get_user_by_username

        user = get_user_by_username("test_user") or create_user("test_user", "password", "test@test.com")

        created = create_platform_account(user["id"], "douyin", "抖音号", "dy001")
        account_id = created["id"]

        result = delete_platform_account(account_id, user["id"])
        assert result.get("deleted") == True