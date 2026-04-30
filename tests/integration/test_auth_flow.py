"""
认证到内容管理完整流程集成测试
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthFlow:
    """测试认证完整流程"""

    def test_register_login_content_flow(self, test_client):
        """测试注册→登录→内容管理流程"""
        # 1. 注册新用户
        register_response = test_client.post(
            "/api/auth/register",
            json={
                "username": "flow_test_user",
                "password": "test_password123",
                "email": "flow@test.com"
            }
        )
        assert register_response.status_code == 200
        register_data = register_response.json()
        assert register_data.get("success") == True
        assert "token" in register_data

        token = register_data["token"]

        # 2. 获取当前用户信息
        me_response = test_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data.get("success") == True
        assert me_data["user"]["username"] == "flow_test_user"

        # 3. 创建内容
        content_response = test_client.post(
            "/api/content",
            json={"title": "认证流程测试", "body": "正文内容", "tags": ["测试"]},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert content_response.status_code == 200
        assert content_response.json().get("success") == True

        # 4. 获取内容列表
        list_response = test_client.get(
            "/api/content",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data.get("success") == True
        assert len(list_data["contents"]) >= 1

    def test_login_with_wrong_password(self, test_client, test_user):
        """测试错误密码无法登录"""
        login_response = test_client.post(
            "/api/auth/login",
            json={
                "username": "test_user",
                "password": "wrong_password"
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data.get("success") == False

    def test_unauthorized_access(self, test_client):
        """测试未授权访问被拒绝"""
        # 无token访问内容
        response = test_client.get("/api/content")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False

        # 无效token访问
        response = test_client.get(
            "/api/content",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == False


class TestUserIsolation:
    """测试用户数据隔离"""

    def test_user_can_only_see_own_content(self, test_client):
        """测试用户只能看到自己的内容"""
        # 用户A注册并创建内容
        user_a_response = test_client.post(
            "/api/auth/register",
            json={
                "username": "user_a",
                "password": "password_a",
                "email": "a@test.com"
            }
        )
        token_a = user_a_response.json()["token"]

        test_client.post(
            "/api/content",
            json={"title": "用户A的内容", "body": "A正文", "tags": []},
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # 用户B注册并创建内容
        user_b_response = test_client.post(
            "/api/auth/register",
            json={
                "username": "user_b",
                "password": "password_b",
                "email": "b@test.com"
            }
        )
        token_b = user_b_response.json()["token"]

        test_client.post(
            "/api/content",
            json={"title": "用户B的内容", "body": "B正文", "tags": []},
            headers={"Authorization": f"Bearer {token_b}"}
        )

        # 用户A获取列表，应该只有自己的内容
        list_a_response = test_client.get(
            "/api/content",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        list_a = list_a_response.json()
        assert all(c["title"] == "用户A的内容" for c in list_a["contents"])

        # 用户B获取列表，应该只有自己的内容
        list_b_response = test_client.get(
            "/api/content",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        list_b = list_b_response.json()
        assert all(c["title"] == "用户B的内容" for c in list_b["contents"])

    def test_user_cannot_access_other_user_content(self, test_client):
        """测试用户不能访问其他用户的内容"""
        # 用户A创建内容
        user_a_response = test_client.post(
            "/api/auth/register",
            json={
                "username": "user_x",
                "password": "password_x",
                "email": "x@test.com"
            }
        )
        token_a = user_a_response.json()["token"]

        create_response = test_client.post(
            "/api/content",
            json={"title": "用户X的私有内容", "body": "X正文", "tags": []},
            headers={"Authorization": f"Bearer {token_a}"}
        )
        content_id = create_response.json()["content"]["id"]

        # 用户B尝试访问
        user_b_response = test_client.post(
            "/api/auth/register",
            json={
                "username": "user_y",
                "password": "password_y",
                "email": "y@test.com"
            }
        )
        token_b = user_b_response.json()["token"]

        access_response = test_client.get(
            f"/api/content/{content_id}",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert access_response.status_code == 200
        access_data = access_response.json()
        assert access_data.get("success") == False
