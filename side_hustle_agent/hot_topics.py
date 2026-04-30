"""
热点话题获取模块

支持获取微博热搜、抖音热榜等平台的热议话题。
"""

import httpx
import asyncio
from typing import Any


class HotTopicsFetcher:
    """热点话题获取器"""

    def __init__(self):
        self.clients: dict[str, httpx.AsyncClient] = {}

    async def get_client(self, base_url: str = "") -> httpx.AsyncClient:
        """获取或创建 HTTP 客户端"""
        key = base_url or "default"
        if key not in self.clients:
            self.clients[key] = httpx.AsyncClient(timeout=30.0)
        return self.clients[key]

    async def fetch_weibo_hot(self) -> dict[str, Any]:
        """
        获取微博热搜榜

        使用免费的微博热搜 API
        """
        try:
            # 尝试多个微博热搜数据源
            sources = [
                "https://api.uomg.com/api/rand.wbhot?format=json",
                "https://tenapi.cn/wbhot/",
            ]

            for url in sources:
                try:
                    client = await self.get_client()
                    response = await client.get(url, follow_redirects=True)
                    if response.status_code == 200:
                        data = response.json()
                        return self._parse_weibo_response(data)
                except Exception:
                    continue

            # 如果所有API都失败，返回模拟数据
            return self._get_mock_weibo_data()

        except Exception as e:
            return {"success": False, "error": str(e), "topics": []}

    def _parse_weibo_response(self, data: dict) -> dict[str, Any]:
        """解析微博API响应"""
        try:
            # 尝试不同的响应格式
            if "data" in data and isinstance(data["data"], list):
                topics = []
                for i, item in enumerate(data["data"][:20], 1):
                    if isinstance(item, dict):
                        topics.append({
                            "rank": i,
                            "title": item.get("word", item.get("name", "")),
                            "hot_value": item.get("hot", item.get("value", 0)),
                            "url": item.get("url", ""),
                        })
                    elif isinstance(item, str):
                        topics.append({
                            "rank": i,
                            "title": item,
                            "hot_value": 0,
                            "url": "",
                        })
                return {"success": True, "topics": topics}

            # 简书/其他格式
            if "code" in data and data["code"] == 1:
                items = data.get("data", {}).get("realtime", [])
                topics = []
                for i, item in enumerate(items[:20], 1):
                    topics.append({
                        "rank": i,
                        "title": item.get("word", ""),
                        "hot_value": item.get("hot", 0),
                        "url": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
                    })
                return {"success": True, "topics": topics}

            return {"success": False, "error": "未知响应格式", "topics": []}
        except Exception as e:
            return {"success": False, "error": str(e), "topics": []}

    def _get_mock_weibo_data(self) -> dict[str, Any]:
        """获取模拟微博热搜数据（用于测试）"""
        mock_topics = [
            {"rank": 1, "title": "五一假期出游攻略", "hot_value": 2856000, "url": ""},
            {"rank": 2, "title": "年轻人副业新趋势", "hot_value": 1920000, "url": ""},
            {"rank": 3, "title": "AI赋能内容创作", "hot_value": 1650000, "url": ""},
            {"rank": 4, "title": "小红书变现技巧", "hot_value": 1430000, "url": ""},
            {"rank": 5, "title": "自媒体月入过万经验", "hot_value": 1280000, "url": ""},
            {"rank": 6, "title": "公众号运营干货", "hot_value": 1150000, "url": ""},
            {"rank": 7, "title": "短视频剪辑教程", "hot_value": 980000, "url": ""},
            {"rank": 8, "title": "内容创业必看指南", "hot_value": 870000, "url": ""},
            {"rank": 9, "title": "平台选择策略", "hot_value": 760000, "url": ""},
            {"rank": 10, "title": "粉丝增长技巧", "hot_value": 650000, "url": ""},
            {"rank": 11, "title": "内容电商运营", "hot_value": 540000, "url": ""},
            {"rank": 12, "title": "私域流量变现", "hot_value": 450000, "url": ""},
            {"rank": 13, "title": "知识付费赛道", "hot_value": 380000, "url": ""},
            {"rank": 14, "title": "IP打造方法论", "hot_value": 320000, "url": ""},
            {"rank": 15, "title": "内容矩阵搭建", "hot_value": 280000, "url": ""},
        ]
        return {"success": True, "topics": mock_topics, "source": "weibo", "mock": True}

    async def fetch_douyin_trending(self) -> dict[str, Any]:
        """
        获取抖音热榜

        注：抖音官方API需要企业资质，这里使用模拟数据
        """
        try:
            # 实际项目中可以接入抖音开放平台 API
            # 这里返回模拟数据
            return self._get_mock_douyin_data()
        except Exception as e:
            return {"success": False, "error": str(e), "topics": []}

    def _get_mock_douyin_data(self) -> dict[str, Any]:
        """获取模拟抖音热榜数据"""
        mock_topics = [
            {"rank": 1, "title": "副业推荐", "hot_value": 985600, "category": "综合"},
            {"rank": 2, "title": "内容创作", "hot_value": 876000, "category": "知识"},
            {"rank": 3, "title": "涨粉技巧", "hot_value": 765000, "category": "运营"},
            {"rank": 4, "title": "变现方式", "hot_value": 654000, "category": "商业"},
            {"rank": 5, "title": "AI工具", "hot_value": 543000, "category": "科技"},
            {"rank": 6, "title": "自媒体教程", "hot_value": 432000, "category": "教育"},
            {"rank": 7, "title": "创业故事", "hot_value": 321000, "category": "人物"},
            {"rank": 8, "title": "赚钱方法", "hot_value": 210000, "category": "商业"},
            {"rank": 9, "title": "小红书运营", "hot_value": 198000, "category": "运营"},
            {"rank": 10, "title": "短视频制作", "hot_value": 165000, "category": "技能"},
        ]
        return {"success": True, "topics": mock_topics, "source": "douyin", "mock": True}

    async def fetch_toutiao_hot(self) -> dict[str, Any]:
        """
        获取头条热榜
        """
        try:
            # 头条热榜 API
            url = "https://api.toutiao888.com/api/tophub/get"
            client = await self.get_client()
            response = await client.get(url, follow_redirects=True)

            if response.status_code == 200:
                data = response.json()
                return self._parse_toutiao_response(data)

            return self._get_mock_toutiao_data()
        except Exception:
            return self._get_mock_toutiao_data()

    def _parse_toutiao_response(self, data: dict) -> dict[str, Any]:
        """解析头条API响应"""
        try:
            if "data" in data and isinstance(data["data"], list):
                topics = []
                for i, item in enumerate(data["data"][:20], 1):
                    if isinstance(item, dict):
                        topics.append({
                            "rank": i,
                            "title": item.get("title", item.get("word", "")),
                            "hot_value": item.get("hot", item.get("value", 0)),
                            "category": item.get("category", ""),
                        })
                return {"success": True, "topics": topics, "source": "toutiao"}
            return {"success": False, "error": "未知响应格式", "topics": []}
        except Exception as e:
            return {"success": False, "error": str(e), "topics": []}

    def _get_mock_toutiao_data(self) -> dict[str, Any]:
        """获取模拟头条热榜数据"""
        mock_topics = [
            {"rank": 1, "title": "副业赚钱新思路", "hot_value": 1560000, "category": "创业"},
            {"rank": 2, "title": "内容创作指南", "hot_value": 1340000, "category": "自媒体"},
            {"rank": 3, "title": "多平台运营策略", "hot_value": 1120000, "category": "运营"},
            {"rank": 4, "title": "粉丝变现技巧", "hot_value": 980000, "category": "商业"},
            {"rank": 5, "title": "AI辅助创作", "hot_value": 870000, "category": "科技"},
            {"rank": 6, "title": "自媒体入门教程", "hot_value": 760000, "category": "教育"},
            {"rank": 7, "title": "内容电商运营", "hot_value": 650000, "category": "电商"},
            {"rank": 8, "title": "私域流量玩法", "hot_value": 540000, "category": "运营"},
            {"rank": 9, "title": "知识付费项目", "hot_value": 430000, "category": "教育"},
            {"rank": 10, "title": "账号定位方法", "hot_value": 320000, "category": "运营"},
        ]
        return {"success": True, "topics": mock_topics, "source": "toutiao", "mock": True}

    async def fetch_all(self) -> dict[str, Any]:
        """获取所有平台的热点话题"""
        results = {}

        # 并发获取各平台数据
        tasks = [
            self.fetch_weibo_hot(),
            self.fetch_douyin_trending(),
            self.fetch_toutiao_hot(),
        ]

        weibo, douyin, toutiao = await asyncio.gather(*tasks, return_exceptions=True)

        if isinstance(weibo, dict):
            results["weibo"] = weibo
        else:
            results["weibo"] = {"success": False, "error": str(weibo), "topics": []}

        if isinstance(douyin, dict):
            results["douyin"] = douyin
        else:
            results["douyin"] = {"success": False, "error": str(douyin), "topics": []}

        if isinstance(toutiao, dict):
            results["toutiao"] = toutiao
        else:
            results["toutiao"] = {"success": False, "error": str(toutiao), "topics": []}

        # 合并所有话题
        all_topics = []
        for source, data in results.items():
            if data.get("success") and data.get("topics"):
                for topic in data["topics"]:
                    topic["source"] = source
                    all_topics.append(topic)

        # 按热度值排序
        all_topics.sort(key=lambda x: x.get("hot_value", 0), reverse=True)

        return {
            "success": True,
            "sources": {
                "weibo": results["weibo"].get("success", False),
                "douyin": results["douyin"].get("success", False),
                "toutiao": results["toutiao"].get("success", False),
            },
            "topics": all_topics[:30],  # 返回前30个最热话题
        }

    async def close(self):
        """关闭所有HTTP客户端"""
        for client in self.clients.values():
            await client.aclose()
        self.clients.clear()


# 全局单例
_fetcher: HotTopicsFetcher | None = None


def get_hot_topics_fetcher() -> HotTopicsFetcher:
    """获取热点话题获取器单例"""
    global _fetcher
    if _fetcher is None:
        _fetcher = HotTopicsFetcher()
    return _fetcher
