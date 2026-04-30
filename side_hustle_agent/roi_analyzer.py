"""
ROI 分析模块

计算内容的投资回报率，分析收益效率。
"""

from typing import Any
from datetime import datetime, timedelta


class ROIAnalyzer:
    """ROI 分析器"""

    def __init__(self):
        # 各平台平均 CPM (每千次阅读收益)
        self.platform_cpm = {
            "wechat_public": 10.0,    # 公众号流量主
            "toutiao": 8.0,           # 头条号
            "xiaohongshu": 15.0,      # 小红书（种草）
            "zhihu": 5.0,             # 知乎
            "baijiahao": 6.0,         # 百家号
            "bilibili": 3.0,          # B站
            "douyin": 2.0,            # 抖音
            "kuaishou": 2.0,          # 快手
            "video_account": 5.0,      # 视频号
        }

        # 各平台平均转化率
        self.platform_conversion = {
            "wechat_public": 0.02,    # 2% 转化到微信
            "toutiao": 0.01,
            "xiaohongshu": 0.03,      # 小红书种草转化较高
            "zhihu": 0.005,
            "baijiahao": 0.01,
            "bilibili": 0.005,
            "douyin": 0.01,
            "kuaishou": 0.015,
            "video_account": 0.02,
        }

    def analyze_content_roi(
        self,
        content_data: dict[str, Any],
        investment: float = 0
    ) -> dict[str, Any]:
        """
        分析单个内容的 ROI

        content_data: {
            "views": int,           # 阅读量
            "likes": int,           # 点赞数
            "comments": int,        # 评论数
            "shares": int,           # 转发数
            "revenue": float,        # 直接收益
            "platform": str,         # 平台
            "cost": float,          # 创作成本（时间价值等）
        }
        """
        views = content_data.get("views", 0)
        likes = content_data.get("likes", 0)
        comments = content_data.get("comments", 0)
        shares = content_data.get("shares", 0)
        revenue = content_data.get("revenue", 0)
        platform = content_data.get("platform", "wechat_public")
        cost = investment or content_data.get("cost", 0)

        # 计算预估收益
        estimated_revenue = self._estimate_revenue(
            views, platform, likes, comments, shares
        )

        # 总收益 = 直接收益 + 预估收益
        total_revenue = revenue + estimated_revenue

        # 计算 ROI
        if cost > 0:
            roi = ((total_revenue - cost) / cost) * 100
        else:
            roi = 0 if total_revenue == 0 else float('inf')

        # 计算 CPM
        cpm = (total_revenue / views * 1000) if views > 0 else 0

        # 计算互动率
        engagement_rate = self._calculate_engagement(views, likes, comments, shares)

        # 评级
        rating = self._get_rating(roi, engagement_rate, views)

        return {
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "direct_revenue": revenue,
            "estimated_revenue": estimated_revenue,
            "total_revenue": total_revenue,
            "cost": cost,
            "roi": round(roi, 2),
            "cpm": round(cpm, 2),
            "engagement_rate": round(engagement_rate, 2),
            "rating": rating,
            "platform": platform,
        }

    def _estimate_revenue(
        self,
        views: int,
        platform: str,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0
    ) -> float:
        """估算间接收益"""
        cpm = self.platform_cpm.get(platform, 5.0)
        conversion = self.platform_conversion.get(platform, 0.01)

        # 基础广告收益
        ad_revenue = views * (cpm / 1000)

        # 互动带来的潜在收益（粗略估算）
        # 点赞、评论、分享可以提升内容曝光，间接增加收益
        engagement_factor = 1 + (likes * 0.01) + (comments * 0.05) + (shares * 0.1)
        engagement_factor = min(engagement_factor, 3.0)  # 上限3倍

        return ad_revenue * engagement_factor

    def _calculate_engagement(
        self,
        views: int,
        likes: int,
        comments: int,
        shares: int
    ) -> float:
        """计算互动率"""
        if views == 0:
            return 0

        total_engagement = likes + comments + shares
        return (total_engagement / views) * 100

    def _get_rating(
        self,
        roi: float,
        engagement_rate: float,
        views: int
    ) -> str:
        """获取内容评级"""
        if views < 100:
            return "D"  # 曝光不足

        if roi == float('inf'):
            return "S"  # 零成本高收益

        if roi >= 100:
            return "A"
        elif roi >= 50:
            return "B"
        elif roi >= 0:
            return "C"
        else:
            return "D"

    def analyze_campaign_roi(
        self,
        contents: list[dict[str, Any]],
        investment: float = 0,
        start_date: str = None,
        end_date: str = None
    ) -> dict[str, Any]:
        """
        分析活动/整体 ROI

        contents: 内容列表
        """
        if not contents:
            return {
                "total_content": 0,
                "total_views": 0,
                "total_revenue": 0,
                "total_cost": investment,
                "roi": 0,
                "avg_cpm": 0,
                "avg_engagement": 0,
                "top_content": None,
                "platform_breakdown": {},
            }

        total_views = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        total_revenue = 0
        platform_stats = {}

        for c in contents:
            views = c.get("views", 0)
            likes = c.get("likes", 0)
            comments = c.get("comments", 0)
            shares = c.get("shares", 0)
            revenue = c.get("revenue", 0)
            platform = c.get("platform", "unknown")

            total_views += views
            total_likes += likes
            total_comments += comments
            total_shares += shares
            total_revenue += revenue

            # 平台分布
            if platform not in platform_stats:
                platform_stats[platform] = {
                    "views": 0,
                    "revenue": 0,
                    "count": 0,
                }
            platform_stats[platform]["views"] += views
            platform_stats[platform]["revenue"] += revenue
            platform_stats[platform]["count"] += 1

        # 计算总体 ROI
        cost = investment
        roi = ((total_revenue - cost) / cost * 100) if cost > 0 else 0

        # 平均 CPM
        avg_cpm = (total_revenue / total_views * 1000) if total_views > 0 else 0

        # 平均互动率
        total_engagement = total_likes + total_comments + total_shares
        avg_engagement = (total_engagement / total_views * 100) if total_views > 0 else 0

        # 找出最佳内容
        top_content = max(contents, key=lambda x: x.get("views", 0)) if contents else None

        # 平台效率排名
        platform_ranking = []
        for platform, stats in platform_stats.items():
            p_cpm = (stats["revenue"] / stats["views"] * 1000) if stats["views"] > 0 else 0
            platform_ranking.append({
                "platform": platform,
                "views": stats["views"],
                "revenue": stats["revenue"],
                "cpm": round(p_cpm, 2),
                "count": stats["count"],
            })
        platform_ranking.sort(key=lambda x: x["cpm"], reverse=True)

        return {
            "total_content": len(contents),
            "total_views": total_views,
            "total_revenue": round(total_revenue, 2),
            "total_cost": investment,
            "roi": round(roi, 2),
            "avg_cpm": round(avg_cpm, 2),
            "avg_engagement": round(avg_engagement, 2),
            "top_content": {
                "id": top_content.get("id") if top_content else None,
                "title": top_content.get("title", "") if top_content else "",
                "views": top_content.get("views", 0) if top_content else 0,
            },
            "platform_breakdown": platform_ranking,
            "date_range": {
                "start": start_date,
                "end": end_date,
            }
        }

    def get_investment_advice(
        self,
        current_roi: float,
        target_roi: float = 50
    ) -> dict[str, Any]:
        """获取投资建议"""
        gap = target_roi - current_roi

        if current_roi >= target_roi:
            return {
                "status": "good",
                "message": "当前 ROI 表现优秀",
                "suggestions": [
                    "继续保持当前策略",
                    "可以适当增加投入扩大规模",
                    "优化高收益内容的生产流程",
                ]
            }

        if gap <= 10:
            return {
                "status": "improve",
                "message": "稍加优化即可达到目标",
                "suggestions": [
                    "提高内容质量，提升阅读量",
                    "优化发布时机，选择流量高峰",
                    "增加互动引导，提升分享率",
                ]
            }

        return {
            "status": "review",
            "message": "需要重新审视内容和策略",
            "suggestions": [
                "分析低ROI内容，减少类似投入",
                "研究高ROI内容的成功因素",
                "考虑平台组合，优化分发策略",
                "控制成本，提升内容效率",
            ]
        }


# 全局单例
_analyzer: ROIAnalyzer | None = None


def get_roi_analyzer() -> ROIAnalyzer:
    """获取 ROI 分析器单例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ROIAnalyzer()
    return _analyzer


def analyze_content_roi(content_data: dict[str, Any], investment: float = 0) -> dict[str, Any]:
    """快捷函数：分析单个内容 ROI"""
    return get_roi_analyzer().analyze_content_roi(content_data, investment)


def analyze_campaign_roi(contents: list[dict[str, Any]], investment: float = 0) -> dict[str, Any]:
    """快捷函数：分析活动 ROI"""
    return get_roi_analyzer().analyze_campaign_roi(contents, investment)
