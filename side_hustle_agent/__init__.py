"""
副业雷达 —— 基于多智能体协同的个性化轻创业推荐系统
"""

__version__ = "0.1.0"

from .orchestrator import SideHustleOrchestrator, create_side_hustle_recommendation

__all__ = [
    "SideHustleOrchestrator",
    "create_side_hustle_recommendation",
]
