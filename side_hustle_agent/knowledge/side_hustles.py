"""
副业数据库
"""

import json
from pathlib import Path
from typing import Literal

from ..core.models import SideHustle, SkillLevel


class SideHustleDatabase:
    """
    副业数据库

    提供副业数据的加载、查询和过滤功能。
    """

    def __init__(self, data_path: str | None = None):
        if data_path is None:
            data_path = Path(__file__).parent / "side_hustles.json"
        self.data_path = Path(data_path)
        self._hustles: list[SideHustle] = []
        self._load()

    def _load(self) -> None:
        """加载数据"""
        if not self.data_path.exists():
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._hustles = [
            SideHustle(**item) for item in data.get("side_hustles", [])
        ]

    def get_all(self) -> list[SideHustle]:
        """获取所有副业"""
        return list(self._hustles)

    def get_by_id(self, id: str) -> SideHustle | None:
        """根据 ID 获取"""
        for h in self._hustles:
            if h.id == id:
                return h
        return None

    def filter(
        self,
        max_startup_cost: int | None = None,
        min_time_hours: float | None = None,
        requires_appearance: bool | None = None,
        city_tier: str | None = None,
        avoid_appearance: bool = False,
        max_learning_curve: SkillLevel | None = None,
    ) -> list[SideHustle]:
        """过滤副业"""
        results = list(self._hustles)

        if max_startup_cost is not None:
            results = [h for h in results if h.startup_cost <= max_startup_cost]

        if min_time_hours is not None:
            results = [h for h in results if h.min_time_hours <= min_time_hours]

        if requires_appearance is not None:
            if requires_appearance:
                results = [h for h in results if h.requires_appearance]
            else:
                results = [h for h in results if not h.requires_appearance]

        if avoid_appearance:
            results = [h for h in results if not h.requires_appearance]

        if city_tier:
            if city_tier in ["一线城市", "二线城市"]:
                pass  # 几乎都适合
            elif city_tier == "三线城市":
                results = [
                    h for h in results
                    if not any(loc in h.location_requirements for loc in ["一线城市"])
                    and h.startup_cost <= 3000
                ]
            else:  # 四线及以下
                results = [
                    h for h in results
                    if not any(loc in h.location_requirements for loc in ["一线城市", "二线城市"])
                    and h.startup_cost <= 2000
                ]

        if max_learning_curve is not None:
            level_map = {
                SkillLevel.NONE: 0,
                SkillLevel.BASIC: 1,
                SkillLevel.INTERMEDIATE: 2,
                SkillLevel.ADVANCED: 3,
            }
            max_level = level_map.get(max_learning_curve, 3)
            results = [
                h for h in results
                if level_map.get(h.learning_curve, 0) <= max_level
            ]

        return results

    def search(self, keyword: str) -> list[SideHustle]:
        """搜索副业"""
        keyword_lower = keyword.lower()
        return [
            h for h in self._hustles
            if keyword_lower in h.name.lower()
            or keyword_lower in h.description.lower()
            or any(keyword_lower in tag.lower() for tag in h.policy_benefits)
        ]

    def get_by_category(self, category: Literal["online", "offline", "hybrid"]) -> list[SideHustle]:
        """按类别获取"""
        if category == "online":
            return [h for h in self._hustles if not h.requires_appearance and not h.location_requirements]
        elif category == "offline":
            return [h for h in self._hustles if h.requires_appearance or h.location_requirements]
        else:  # hybrid
            return [h for h in self._hustles if not h.requires_appearance and h.location_requirements]


# 全局数据库实例
_database: SideHustleDatabase | None = None


def get_side_hustle_database() -> SideHustleDatabase:
    """获取副业数据库单例"""
    global _database
    if _database is None:
        _database = SideHustleDatabase()
    return _database