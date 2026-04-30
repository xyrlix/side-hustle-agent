"""
API 端点单元测试
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """测试健康检查端点"""

    def test_health_check(self, test_client):
        """测试健康检查"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok" or data.get("status") == "healthy" or "message" in data


class TestAuthEndpoints:
    """测试认证相关端点"""

    def test_register(self, test_client):
        """测试用户注册"""
        response = test_client.post(
            "/api/auth/register",
            json={"username": "newuser123", "password": "password123", "email": "new@test.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "token" in data

    def test_register_duplicate_username(self, test_client, test_user):
        """测试重复用户名注册"""
        response = test_client.post(
            "/api/auth/register",
            json={"username": "test_user", "password": "password", "email": "test@test.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False
        assert "error" in data.get("message", "").lower() or not data.get("success")

    def test_login(self, test_client, test_user):
        """测试用户登录"""
        response = test_client.post(
            "/api/auth/login",
            json={"username": "test_user", "password": "test_password"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "token" in data

    def test_login_wrong_password(self, test_client, test_user):
        """测试错误密码登录"""
        response = test_client.post(
            "/api/auth/login",
            json={"username": "test_user", "password": "wrongpassword"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False

    def test_get_me(self, test_client, auth_token):
        """测试获取当前用户信息"""
        response = test_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "user" in data


class TestContentEndpoints:
    """测试内容管理端点"""

    def test_create_content(self, test_client, auth_token):
        """测试创建内容"""
        response = test_client.post(
            "/api/content",
            json={
                "title": "测试内容",
                "body": "这是测试内容正文",
                "summary": "摘要",
                "tags": ["测试"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "content" in data
        assert data["content"]["title"] == "测试内容"

    def test_get_contents(self, test_client, auth_token):
        """测试获取内容列表"""
        # 先创建内容
        test_client.post(
            "/api/content",
            json={"title": "列表测试", "body": "正文", "tags": []},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # 获取列表
        response = test_client.get(
            "/api/content",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "contents" in data

    def test_get_content_by_id(self, test_client, auth_token):
        """测试获取单个内容"""
        # 先创建
        create_response = test_client.post(
            "/api/content",
            json={"title": "单个测试", "body": "正文", "tags": []},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        content_id = create_response.json()["content"]["id"]

        # 获取详情
        response = test_client.get(
            f"/api/content/{content_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data["content"]["title"] == "单个测试"

    def test_update_content(self, test_client, auth_token):
        """测试更新内容"""
        # 先创建
        create_response = test_client.post(
            "/api/content",
            json={"title": "待更新", "body": "正文", "tags": []},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        content_id = create_response.json()["content"]["id"]

        # 更新
        response = test_client.put(
            f"/api/content/{content_id}",
            json={"title": "已更新"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_delete_content(self, test_client, auth_token):
        """测试删除内容"""
        # 先创建
        create_response = test_client.post(
            "/api/content",
            json={"title": "待删除", "body": "正文", "tags": []},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        content_id = create_response.json()["content"]["id"]

        # 删除
        response = test_client.delete(
            f"/api/content/{content_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_unauthorized_content_access(self, test_client):
        """测试未授权访问内容"""
        response = test_client.get("/api/content")
        assert response.status_code == 200
        data = response.json()
        # 应该返回未登录错误
        assert data.get("success") == False


class TestPlatformEndpoints:
    """测试平台相关端点"""

    def test_get_platforms(self, test_client):
        """测试获取平台列表"""
        response = test_client.get("/api/platforms")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "platforms" in data
        assert len(data["platforms"]) > 0

    def test_create_platform_account(self, test_client, auth_token):
        """测试创建平台账号"""
        response = test_client.post(
            "/api/platforms/accounts",
            json={
                "platform": "wechat_public",
                "account_name": "我的公众号",
                "account_id": "wx_test123"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_get_platform_accounts(self, test_client, auth_token):
        """测试获取平台账号列表"""
        response = test_client.get(
            "/api/platforms/accounts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "accounts" in data


class TestCampaignEndpoints:
    """测试活动管理端点"""

    def test_create_campaign(self, test_client, auth_token):
        """测试创建活动"""
        response = test_client.post(
            "/api/campaigns",
            json={
                "name": "测试活动",
                "description": "活动描述"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True

    def test_get_campaigns(self, test_client, auth_token):
        """测试获取活动列表"""
        response = test_client.get(
            "/api/campaigns",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True


class TestAnalyticsEndpoints:
    """测试数据统计端点"""

    def test_get_analytics_summary(self, test_client, auth_token):
        """测试获取统计摘要"""
        response = test_client.get(
            "/api/analytics/summary",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "summary" in data


class TestConfigEndpoints:
    """测试配置端点"""

    def test_get_config(self, test_client):
        """测试获取配置"""
        response = test_client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "llm_provider" in data

    def test_get_models(self, test_client):
        """测试获取模型列表"""
        response = test_client.get("/api/models?provider=deepseek")
        assert response.status_code == 200


class TestRecommendEndpoints:
    """测试副业推荐端点（无需认证）"""

    def test_recommend(self, test_client, sample_user_input):
        """测试副业推荐"""
        response = test_client.post(
            "/api/recommend",
            json=sample_user_input.model_dump()
        )
        # 可能因为没有 API key 而失败，但应该返回结构化响应
        assert response.status_code in [200, 500]
        data = response.json()
        # 返回 success 或者有错误信息
        assert "success" in data or "error" in data