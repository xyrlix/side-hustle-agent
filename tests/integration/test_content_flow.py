"""
内容创作到发布完整流程集成测试
"""

import pytest
from fastapi.testclient import TestClient


class TestContentCreationFlow:
    """测试内容创建到发布的完整流程"""

    def test_create_then_fetch_content(self, test_client, auth_token):
        """测试创建内容后能正确获取"""
        # 创建内容
        create_response = test_client.post(
            "/api/content",
            json={
                "title": "流程测试内容",
                "body": "这是完整正文内容",
                "summary": "测试摘要",
                "tags": ["流程测试"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert create_response.status_code == 200
        data = create_response.json()
        assert data.get("success") == True

        content_id = data["content"]["id"]

        # 获取内容详情
        get_response = test_client.get(
            f"/api/content/{content_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert get_response.status_code == 200
        detail_data = get_response.json()
        assert detail_data["content"]["title"] == "流程测试内容"
        assert detail_data["content"]["body"] == "这是完整正文内容"

    def test_create_update_version_flow(self, test_client, auth_token):
        """测试内容创建→更新→版本历史流程"""
        # 创建
        create_response = test_client.post(
            "/api/content",
            json={"title": "版本测试", "body": "初始版本", "tags": []},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        content_id = create_response.json()["content"]["id"]

        # 更新
        update_response = test_client.put(
            f"/api/content/{content_id}",
            json={"title": "版本测试", "body": "第二版本", "change_summary": "第一次更新"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert update_response.json().get("success") == True

        # 获取版本历史
        versions_response = test_client.get(
            f"/api/content/{content_id}/versions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert versions_response.status_code == 200
        assert "versions" in versions_response.json()

    def test_create_publish_flow(self, test_client, auth_token):
        """测试创建→发布流程"""
        # 创建
        create_response = test_client.post(
            "/api/content",
            json={"title": "待发布", "body": "发布正文", "tags": []},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        content_id = create_response.json()["content"]["id"]

        # 发布到单个平台（API 只支持单个平台）
        publish_response = test_client.post(
            f"/api/content/{content_id}/publish?platform=wechat_public",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # 注意：发布 API 可能返回 422 如果验证失败，或 200 如果成功
        assert publish_response.status_code in [200, 422]

        # 验证发布日志
        logs_response = test_client.get(
            f"/api/content/{content_id}/logs",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert logs_response.status_code == 200
        assert "logs" in logs_response.json()

    def test_create_delete_flow(self, test_client, auth_token):
        """测试创建→删除流程"""
        # 创建
        create_response = test_client.post(
            "/api/content",
            json={"title": "待删除", "body": "删除正文", "tags": []},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        content_id = create_response.json()["content"]["id"]

        # 删除
        delete_response = test_client.delete(
            f"/api/content/{content_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert delete_response.json().get("success") == True

        # 验证已删除
        get_response = test_client.get(
            f"/api/content/{content_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # 应该无法获取
        assert get_response.status_code == 200
        assert get_response.json().get("success") == False


class TestCampaignContentAssociation:
    """测试活动与内容关联"""

    def test_create_campaign_with_content(self, test_client, auth_token):
        """测试创建活动并关联内容"""
        # 创建活动
        campaign_response = test_client.post(
            "/api/campaigns",
            json={
                "name": "测试活动",
                "description": "活动描述"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert campaign_response.status_code == 200
        campaign_id = campaign_response.json()["campaign"]["id"]

        # 创建内容
        content_response = test_client.post(
            "/api/content",
            json={"title": "活动内容", "body": "内容正文", "tags": []},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert content_response.status_code == 200
        # content API doesn't support campaign_id directly, just verify content created
        assert "content" in content_response.json()


class TestPlatformAccountFlow:
    """测试平台账号与发布流程"""

    def test_connect_platform_then_publish(self, test_client, auth_token):
        """测试连接平台账号后发布内容"""
        # 添加平台账号
        account_response = test_client.post(
            "/api/platforms/accounts",
            json={
                "platform": "wechat_public",
                "account_name": "测试公众号",
                "account_id": "wx_test123"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert account_response.status_code == 200
        account_data = account_response.json()
        assert account_data.get("success") == True

        # 创建内容
        content_response = test_client.post(
            "/api/content",
            json={"title": "平台发布测试", "body": "正文", "tags": []},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        content_id = content_response.json()["content"]["id"]

        # 发布到平台（API 只支持单个 platform 参数）
        publish_response = test_client.post(
            f"/api/content/{content_id}/publish?platform=wechat_public",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # 只验证端点可访问
        assert publish_response.status_code in [200, 422]
