"""
Playwright 配置
"""

import pytest
from playwright.sync_api import sync_playwright, Browser, Page


@pytest.fixture(scope="session")
def browser():
    """创建浏览器实例"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def browser_context(browser: Browser):
    """创建浏览器上下文"""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture
def page(browser_context):
    """创建新页面"""
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture
def api_client():
    """API 客户端辅助函数"""
    import requests

    class APIClient:
        def __init__(self, base_url="http://localhost:8000"):
            self.base_url = base_url
            self.token = None

        def register(self, username, password, email):
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json={"username": username, "password": password, "email": email}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data.get("token")
            return response

        def login(self, username, password):
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data.get("token")
            return response

        def create_content(self, title, body, tags=None):
            response = requests.post(
                f"{self.base_url}/api/content",
                json={"title": title, "body": body, "tags": tags or []},
                headers={"Authorization": f"Bearer {self.token}"} if self.token else {}
            )
            return response

        def get_contents(self):
            response = requests.get(
                f"{self.base_url}/api/content",
                headers={"Authorization": f"Bearer {self.token}"} if self.token else {}
            )
            return response

    return APIClient()
