"""
热点话题获取模块

支持获取微博热搜、抖音热榜、头条热榜等平台的真实热议话题。
使用多数据源 + 缓存降级机制确保稳定性。
"""

import httpx
import asyncio
import time
import random
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Topic:
    """话题数据模型"""
    rank: int
    title: str
    hot_value: int
    url: str = ""
    category: str = ""
    source: str = ""
    fetched_at: str = ""


@dataclass
class HotTopicsResult:
    """热点话题结果"""
    success: bool
    topics: list[Topic] = field(default_factory=list)
    source: str = ""
    mock: bool = False
    error: str = ""
    fetched_at: str = ""


class HotTopicsFetcher:
    """热点话题获取器 - 支持多数据源、自动降级、缓存"""

    # 微博热搜 API 列表（按优先级排序）
    WEIBO_SOURCES = [
        # 微博移动端热搜API
        {"url": "https://weibo.com/ajax/statuses/hot_band", "type": "ajax"},
        # 微博话题榜单
        {"url": "https://weibo.com/ajax/side/hotSearch", "type": "json"},
    ]

    # 抖音热榜 API
    DOUYIN_SOURCES = [
        # 抖音热点榜
        {"url": "https://www.douyin.com/aweme/v1/web/trending/search/list/", "type": "api"},
    ]

    # 头条热榜 API
    TOUTIAO_SOURCES = [
        # 头条热榜
        {"url": "https://api.toutiao888.com/api/tophub/get", "type": "json"},
    ]

    def __init__(self, cache_duration: int = 300):
        """
        初始化热点话题获取器

        Args:
            cache_duration: 缓存有效期（秒），默认5分钟
        """
        self.cache_duration = cache_duration
        self._cache: dict[str, tuple[datetime, HotTopicsResult]] = {}
        self.clients: dict[str, httpx.AsyncClient] = {}
        self._lock = asyncio.Lock()

    async def get_client(self, base_url: str = "") -> httpx.AsyncClient:
        """获取或创建 HTTP 客户端"""
        key = base_url or "default"
        if key not in self.clients:
            self.clients[key] = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Referer": "https://weibo.com",
                }
            )
        return self.clients[key]

    def _is_cache_valid(self, source: str) -> bool:
        """检查缓存是否有效"""
        if source not in self._cache:
            return False
        cached_time, _ = self._cache[source]
        return (datetime.now() - cached_time).seconds < self.cache_duration

    def _get_cache(self, source: str) -> HotTopicsResult | None:
        """获取缓存数据"""
        if self._is_cache_valid(source):
            _, result = self._cache[source]
            return result
        return None

    def _set_cache(self, source: str, result: HotTopicsResult):
        """设置缓存"""
        self._cache[source] = (datetime.now(), result)

    async def fetch_weibo_hot(self, force_refresh: bool = False) -> dict[str, Any]:
        """
        获取微博热搜榜

        使用多数据源 + 缓存降级机制
        """
        # 检查缓存
        if not force_refresh:
            cached = self._get_cache("weibo")
            if cached:
                return {
                    "success": cached.success,
                    "topics": [t.__dict__ for t in cached.topics],
                    "source": cached.source,
                    "mock": cached.mock,
                    "cached": True,
                }

        async with self._lock:
            # 双重检查
            if not force_refresh:
                cached = self._get_cache("weibo")
                if cached:
                    return {
                        "success": cached.success,
                        "topics": [t.__dict__ for t in cached.topics],
                        "source": cached.source,
                        "mock": cached.mock,
                        "cached": True,
                    }

            result = await self._fetch_weibo_with_fallback()
            # 缓存结果
            self._set_cache("weibo", result)
            return {
                "success": result.success,
                "topics": [t.__dict__ for t in result.topics],
                "source": result.source,
                "mock": result.mock,
                "error": result.error,
            }

    async def _fetch_weibo_with_fallback(self) -> HotTopicsResult:
        """降级获取微博热搜"""
        # 尝试多个数据源
        sources_tried = []

        for source_config in self.WEIBO_SOURCES:
            try:
                result = await self._try_weibo_source(source_config)
                if result.success and result.topics:
                    return result
                sources_tried.append(source_config["url"])
            except Exception as e:
                sources_tried.append(f"{source_config['url']}: {str(e)}")
                continue

        # 所有数据源都失败，返回降级数据（但标记为mock）
        return self._get_fallback_weibo_data()

    async def _try_weibo_source(self, source_config: dict) -> HotTopicsResult:
        """尝试单个微博数据源"""
        url = source_config["url"]
        client = await self.get_client()

        try:
            response = await client.get(url, follow_redirects=True)

            if response.status_code != 200:
                return HotTopicsResult(success=False, error=f"HTTP {response.status_code}")

            data = response.json()

            # 解析微博移动端热搜格式
            if "data" in data and "band_list" in data["data"]:
                topics = []
                for i, item in enumerate(data["data"]["band_list"][:20], 1):
                    if isinstance(item, dict):
                        topics.append(Topic(
                            rank=i,
                            title=item.get("word", item.get("search_word", "")),
                            hot_value=item.get("hot_value", 0),
                            url=f"https://s.weibo.com/weibo?q={item.get('word', '')}",
                            source="weibo",
                            fetched_at=datetime.now().isoformat()
                        ))
                return HotTopicsResult(success=True, topics=topics, source="weibo")

            # 解析微博热搜API格式
            if "data" in data and "realtime" in data["data"]:
                topics = []
                for i, item in enumerate(data["data"]["realtime"][:20], 1):
                    if isinstance(item, dict):
                        topics.append(Topic(
                            rank=i,
                            title=item.get("word", item.get("note", "")),
                            hot_value=item.get("hot", item.get("value", 0)),
                            url=f"https://s.weibo.com/weibo?q={item.get('word', '')}",
                            source="weibo",
                            fetched_at=datetime.now().isoformat()
                        ))
                return HotTopicsResult(success=True, topics=topics, source="weibo")

            return HotTopicsResult(success=False, error="未知响应格式")

        except Exception as e:
            return HotTopicsResult(success=False, error=str(e))

    def _get_fallback_weibo_data(self) -> HotTopicsResult:
        """
        获取降级微博热搜数据（基于真实热点话题规律生成）

        注：仅在API不可用时使用，内容为合理化的模拟数据
        """
        # 基于真实规律的热点话题（副业/创业/自媒体相关）
        mock_topics = [
            {"rank": 1, "title": "年轻人最喜欢的副业有哪些", "hot_value": 2856000, "url": "https://s.weibo.com/weibo?q=年轻人最喜欢的副业"},
            {"rank": 2, "title": "自媒体创业月入过万真实吗", "hot_value": 2650000, "url": "https://s.weibo.com/weibo?q=自媒体创业"},
            {"rank": 3, "title": "小红书博主真实收入揭秘", "hot_value": 2430000, "url": "https://s.weibo.com/weibo?q=小红书博主收入"},
            {"rank": 4, "title": "AI创作工具使用教程", "hot_value": 2280000, "url": "https://s.weibo.com/weibo?q=AI创作"},
            {"rank": 5, "title": "副业赚钱的N种方式", "hot_value": 2150000, "url": "https://s.weibo.com/weibo?q=副业赚钱"},
            {"rank": 6, "title": "短视频剪辑接单平台", "hot_value": 1980000, "url": "https://s.weibo.com/weibo?q=短视频剪辑接单"},
            {"rank": 7, "title": "知识付费项目推荐", "hot_value": 1870000, "url": "https://s.weibo.com/weibo?q=知识付费"},
            {"rank": 8, "title": "公众号运营从0到1", "hot_value": 1760000, "url": "https://s.weibo.com/weibo?q=公众号运营"},
            {"rank": 9, "title": "私域流量变现技巧", "hot_value": 1650000, "url": "https://s.weibo.com/weibo?q=私域流量变现"},
            {"rank": 10, "title": "内容创业必看干货", "hot_value": 1540000, "url": "https://s.weibo.com/weibo?q=内容创业"},
            {"rank": 11, "title": "抖音带货实操教程", "hot_value": 1430000, "url": "https://s.weibo.com/weibo?q=抖音带货教程"},
            {"rank": 12, "title": "闲鱼二手商品赚钱攻略", "hot_value": 1320000, "url": "https://s.weibo.com/weibo?q=闲鱼赚钱"},
            {"rank": 13, "title": "跨境电商创业分享", "hot_value": 1210000, "url": "https://s.weibo.com/weibo?q=跨境电商创业"},
            {"rank": 14, "title": "兼职翻译平台推荐", "hot_value": 1100000, "url": "https://s.weibo.com/weibo?q=翻译兼职"},
            {"rank": 15, "title": "设计师接单渠道", "hot_value": 990000, "url": "https://s.weibo.com/weibo?q=设计师接单"},
            {"rank": 16, "title": "编程外包项目平台", "hot_value": 880000, "url": "https://s.weibo.com/weibo?q=编程外包"},
            {"rank": 17, "title": "播客录制变现方式", "hot_value": 770000, "url": "https://s.weibo.com/weibo?q=播客变现"},
            {"rank": 18, "title": "直播带货入门指南", "hot_value": 660000, "url": "https://s.weibo.com/weibo?q=直播带货入门"},
            {"rank": 19, "title": "电商选品技巧分享", "hot_value": 550000, "url": "https://s.weibo.com/weibo?q=电商选品"},
            {"rank": 20, "title": "线上教育创业模式", "hot_value": 440000, "url": "https://s.weibo.com/weibo?q=线上教育创业"},
        ]
        topics = [
            Topic(
                rank=t["rank"],
                title=t["title"],
                hot_value=t["hot_value"],
                url=t["url"],
                source="weibo",
                fetched_at=datetime.now().isoformat()
            )
            for t in mock_topics
        ]
        return HotTopicsResult(success=True, topics=topics, source="weibo", mock=True)

    async def fetch_douyin_trending(self, force_refresh: bool = False) -> dict[str, Any]:
        """
        获取抖音热榜

        使用多数据源 + 缓存降级机制
        """
        # 检查缓存
        if not force_refresh:
            cached = self._get_cache("douyin")
            if cached:
                return {
                    "success": cached.success,
                    "topics": [t.__dict__ for t in cached.topics],
                    "source": cached.source,
                    "mock": cached.mock,
                    "cached": True,
                }

        async with self._lock:
            if not force_refresh:
                cached = self._get_cache("douyin")
                if cached:
                    return {
                        "success": cached.success,
                        "topics": [t.__dict__ for t in cached.topics],
                        "source": cached.source,
                        "mock": cached.mock,
                        "cached": True,
                    }

            result = await self._fetch_douyin_with_fallback()
            self._set_cache("douyin", result)
            return {
                "success": result.success,
                "topics": [t.__dict__ for t in result.topics],
                "source": result.source,
                "mock": result.mock,
                "error": result.error,
            }

    async def _fetch_douyin_with_fallback(self) -> HotTopicsResult:
        """降级获取抖音热榜"""
        for source_config in self.DOUYIN_SOURCES:
            try:
                result = await self._try_douyin_source(source_config)
                if result.success and result.topics:
                    return result
            except Exception:
                continue

        return self._get_fallback_douyin_data()

    async def _try_douyin_source(self, source_config: dict) -> HotTopicsResult:
        """尝试单个抖音数据源"""
        client = await self.get_client("https://www.douyin.com")

        try:
            # 抖音网页版热榜
            response = await client.get(
                "https://www.douyin.com/aweme/v1/web/trending/search/list/",
                params={
                    "keyword": "",
                    "search_source": "normal_search",
                    "query_correct_type": "1",
                },
                follow_redirects=True
            )

            if response.status_code == 200:
                data = response.json()
                if "trending_list" in data:
                    topics = []
                    for i, item in enumerate(data["trending_list"][:20], 1):
                        topics.append(Topic(
                            rank=i,
                            title=item.get("word", item.get("title", "")),
                            hot_value=item.get("hot_value", 0),
                            category=item.get("category", ""),
                            source="douyin",
                            fetched_at=datetime.now().isoformat()
                        ))
                    return HotTopicsResult(success=True, topics=topics, source="douyin")

            return HotTopicsResult(success=False, error="响应格式错误")

        except Exception as e:
            return HotTopicsResult(success=False, error=str(e))

    def _get_fallback_douyin_data(self) -> HotTopicsResult:
        """获取降级抖音热榜数据"""
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
            {"rank": 11, "title": "直播带货", "hot_value": 154000, "category": "电商"},
            {"rank": 12, "title": "私域流量", "hot_value": 143000, "category": "运营"},
            {"rank": 13, "title": "知识付费", "hot_value": 132000, "category": "教育"},
            {"rank": 14, "title": "账号运营", "hot_value": 121000, "category": "运营"},
            {"rank": 15, "title": "选品技巧", "hot_value": 110000, "category": "电商"},
        ]
        topics = [
            Topic(
                rank=t["rank"],
                title=t["title"],
                hot_value=t["hot_value"],
                category=t.get("category", ""),
                source="douyin",
                fetched_at=datetime.now().isoformat()
            )
            for t in mock_topics
        ]
        return HotTopicsResult(success=True, topics=topics, source="douyin", mock=True)

    async def fetch_toutiao_hot(self, force_refresh: bool = False) -> dict[str, Any]:
        """获取头条热榜"""
        if not force_refresh:
            cached = self._get_cache("toutiao")
            if cached:
                return {
                    "success": cached.success,
                    "topics": [t.__dict__ for t in cached.topics],
                    "source": cached.source,
                    "mock": cached.mock,
                    "cached": True,
                }

        async with self._lock:
            if not force_refresh:
                cached = self._get_cache("toutiao")
                if cached:
                    return {
                        "success": cached.success,
                        "topics": [t.__dict__ for t in cached.topics],
                        "source": cached.source,
                        "mock": cached.mock,
                        "cached": True,
                    }

            result = await self._fetch_toutiao_with_fallback()
            self._set_cache("toutiao", result)
            return {
                "success": result.success,
                "topics": [t.__dict__ for t in result.topics],
                "source": result.source,
                "mock": result.mock,
                "error": result.error,
            }

    async def _fetch_toutiao_with_fallback(self) -> HotTopicsResult:
        """降级获取头条热榜"""
        for source_config in self.TOUTIAO_SOURCES:
            try:
                result = await self._try_toutiao_source(source_config)
                if result.success and result.topics:
                    return result
            except Exception:
                continue

        return self._get_fallback_toutiao_data()

    async def _try_toutiao_source(self, source_config: dict) -> HotTopicsResult:
        """尝试单个头条数据源"""
        url = source_config["url"]
        client = await self.get_client()

        try:
            response = await client.get(url, follow_redirects=True)

            if response.status_code == 200:
                data = response.json()
                if "data" in data and isinstance(data["data"], list):
                    topics = []
                    for i, item in enumerate(data["data"][:20], 1):
                        if isinstance(item, dict):
                            topics.append(Topic(
                                rank=i,
                                title=item.get("title", item.get("word", "")),
                                hot_value=item.get("hot", item.get("value", 0)),
                                category=item.get("category", ""),
                                source="toutiao",
                                fetched_at=datetime.now().isoformat()
                            ))
                    return HotTopicsResult(success=True, topics=topics, source="toutiao")

            return HotTopicsResult(success=False, error="响应格式错误")

        except Exception as e:
            return HotTopicsResult(success=False, error=str(e))

    def _get_fallback_toutiao_data(self) -> HotTopicsResult:
        """获取降级头条热榜数据"""
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
            {"rank": 11, "title": "爆款内容技巧", "hot_value": 280000, "category": "运营"},
            {"rank": 12, "title": "平台选择攻略", "hot_value": 240000, "category": "运营"},
            {"rank": 13, "title": "写作变现方法", "hot_value": 200000, "category": "商业"},
            {"rank": 14, "title": "视频剪辑接单", "hot_value": 180000, "category": "技能"},
            {"rank": 15, "title": "创业项目推荐", "hot_value": 160000, "category": "创业"},
        ]
        topics = [
            Topic(
                rank=t["rank"],
                title=t["title"],
                hot_value=t["hot_value"],
                category=t.get("category", ""),
                source="toutiao",
                fetched_at=datetime.now().isoformat()
            )
            for t in mock_topics
        ]
        return HotTopicsResult(success=True, topics=topics, source="toutiao", mock=True)

    async def fetch_all(self, force_refresh: bool = False) -> dict[str, Any]:
        """获取所有平台的热点话题"""
        results = {}

        # 并发获取各平台数据
        tasks = [
            self.fetch_weibo_hot(force_refresh),
            self.fetch_douyin_trending(force_refresh),
            self.fetch_toutiao_hot(force_refresh),
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
            "topics": all_topics[:30],
            "has_mock_data": any(data.get("mock", False) for data in results.values()),
        }

    def clear_cache(self):
        """清除所有缓存"""
        self._cache.clear()

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
        _fetcher = HotTopicsFetcher(cache_duration=300)  # 5分钟缓存
    return _fetcher