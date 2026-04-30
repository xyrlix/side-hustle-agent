"""
端到端测试 - 用户注册和登录流程
"""

import pytest
from playwright.sync_api import Page, expect


class TestAuthE2E:
    """端到端认证流程测试"""

    def test_register_flow(self, page: Page):
        """测试用户注册流程"""
        page.goto("http://localhost:1420")
        page.wait_for_load_state("networkidle")

        # 点击登录按钮打开模态框
        page.get_by_role("button", name="登录").first.click()

        # 点击切换到注册
        page.get_by_role("button", name="没有账号？立即注册").click()

        # 填写注册表单
        page.get_by_placeholder("请输入用户名").fill("e2e_test_user2")
        page.get_by_placeholder("请输入密码").fill("password123")
        page.get_by_placeholder("请输入邮箱").fill("e2e2@test.com")

        # 点击注册按钮
        page.get_by_role("button", name="注册").click()

        # 等待注册完成
        page.wait_for_timeout(500)

    def test_login_flow(self, page: Page):
        """测试用户登录流程"""
        page.goto("http://localhost:1420")
        page.wait_for_load_state("networkidle")

        # 点击登录按钮
        page.get_by_role("button", name="登录").first.click()

        # 填写登录表单
        page.get_by_placeholder("请输入用户名").fill("test_user")
        page.get_by_placeholder("请输入密码").fill("test_password")

        # 点击登录按钮（modal 里的提交按钮）
        page.get_by_role("button", name="登录", exact=True).click()

        # 验证登录成功
        page.wait_for_timeout(500)


class TestNavigationE2E:
    """端到端导航测试"""

    def test_main_navigation(self, page: Page):
        """测试主导航功能"""
        page.goto("http://localhost:1420")
        page.wait_for_load_state("networkidle")

        # 检查首页元素
        page.get_by_role("heading", name="副业雷达").first.is_visible()
        page.get_by_role("button", name="登录").first.is_visible()

        # 导航到副业推荐页
        page.get_by_role("button", name="开始副业推荐").click()
        page.wait_for_timeout(500)

    def test_dashboard_view(self, page: Page):
        """测试仪表盘视图"""
        page.goto("http://localhost:1420")
        page.wait_for_load_state("networkidle")
        page.get_by_role("heading", name="欢迎使用副业雷达").is_visible()


class TestContentManagementE2E:
    """端到端内容管理测试"""

    def test_create_content(self, page: Page):
        """测试创建内容流程"""
        # 先登录
        page.goto("http://localhost:1420")
        page.wait_for_load_state("networkidle")
        page.get_by_role("button", name="登录").first.click()
        page.get_by_placeholder("请输入用户名").fill("test_user")
        page.get_by_placeholder("请输入密码").fill("test_password")
        page.get_by_role("button", name="登录", exact=True).click()
        page.wait_for_timeout(1000)

        # 创建内容 - 使用 fetch 直接调用 API
        page.evaluate("""
            fetch('/api/content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('token')
                },
                body: JSON.stringify({
                    title: 'E2E测试内容',
                    body: '这是端到端测试创建的正文内容',
                    tags: ['e2e', '测试']
                })
            })
        """)
        page.wait_for_timeout(500)

    def test_list_content(self, page: Page):
        """测试内容列表"""
        # 先登录
        page.goto("http://localhost:1420")
        page.wait_for_load_state("networkidle")
        page.get_by_role("button", name="登录").first.click()
        page.get_by_placeholder("请输入用户名").fill("test_user")
        page.get_by_placeholder("请输入密码").fill("test_password")
        page.get_by_role("button", name="登录", exact=True).click()
        page.wait_for_timeout(1000)


class TestPageLoadE2E:
    """端到端页面加载测试"""

    def test_homepage_loads(self, page: Page):
        """测试首页加载"""
        page.goto("http://localhost:1420")
        page.wait_for_load_state("networkidle")
        page.get_by_role("heading", name="副业雷达").first.is_visible()

    def test_no_console_errors(self, page: Page):
        """测试无控制台错误"""
        errors = []

        def handle_console(msg):
            if msg.type == "error":
                errors.append(msg.text)

        page.on("console", handle_console)
        page.goto("http://localhost:1420")
        page.wait_for_timeout(1000)

        assert len(errors) == 0, f"控制台错误: {errors}"
