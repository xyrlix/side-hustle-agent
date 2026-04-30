"""
内容违规词检测模块

检测文本中的违规词、广告词、敏感词等。
"""

import re
from typing import Any


class ContentFilter:
    """内容过滤器"""

    # 违规词类别
    SENSITIVE_WORDS = {
        # 政治敏感
        "政治相关": ["敏感词1", "敏感词2"],  # 实际项目中应接入官方敏感词库
        # 虚假广告
        "虚假广告": ["最高级", "绝对", "100%"],
        # 医疗相关
        "医疗违规": ["根治", "特效药", "包治"],
    }

    # 广告违规词
    AD_WORDS = [
        "最", "第一", "顶级", "极致", "至臻", "独家", "唯一",
        "首选", "国家级", "世界级", "全网", "独家",
        "投资回报率", "稳赚", "保本", "零风险",
    ]

    # 平台限流敏感词
    PLATFORM_LIMIT_WORDS = [
        "微信", "公众号", "抖音", "小红书", "知乎", "微博",
        "外部链接", "私聊", "加我", "联系方式",
    ]

    def __init__(self):
        self.ad_pattern = self._build_pattern(self.AD_WORDS)
        self.limit_pattern = self._build_pattern(self.PLATFORM_LIMIT_WORDS)

    def _build_pattern(self, words: list[str]) -> re.Pattern:
        """构建正则匹配模式"""
        escaped = [re.escape(w) for w in words]
        return re.compile("|".join(escaped), re.IGNORECASE)

    def check(self, text: str) -> dict[str, Any]:
        """
        检测文本内容

        返回: {
            "passed": bool,           # 是否通过检测
            "violations": [           # 违规列表
                {
                    "type": str,       # violation/ad/limit
                    "category": str,   # 违规类别
                    "word": str,       # 违规词
                    "position": int,   # 位置
                }
            ],
            "summary": str,           # 检测摘要
            "score": int,             # 内容质量分数 (0-100)
        }
        """
        if not text:
            return {
                "passed": True,
                "violations": [],
                "summary": "内容为空",
                "score": 100,
            }

        violations = []
        text_lower = text.lower()

        # 检测广告词
        ad_matches = self.ad_pattern.finditer(text)
        for match in ad_matches:
            violations.append({
                "type": "ad",
                "category": "广告违规",
                "word": match.group(),
                "position": match.start(),
            })

        # 检测平台限流词
        limit_matches = self.limit_pattern.finditer(text)
        for match in limit_matches:
            violations.append({
                "type": "limit",
                "category": "平台限流风险",
                "word": match.group(),
                "position": match.start(),
            })

        # 检测特殊字符
        special_chars = re.findall(r'[☆★◆◇●○■□△▲▽▼]', text)
        if len(special_chars) > 10:
            violations.append({
                "type": "style",
                "category": "特殊字符过多",
                "word": f"包含{len(special_chars)}个特殊符号",
                "position": 0,
            })

        # 检测重复内容
        duplicated = self._check_duplication(text)
        if duplicated:
            violations.append({
                "type": "quality",
                "category": "内容重复",
                "word": duplicated,
                "position": 0,
            })

        # 计算内容质量分数
        score = self._calculate_score(text, violations)

        # 判断是否通过
        # 1个violation扣10分，ad类型violation直接fail
        ad_violations = [v for v in violations if v["type"] == "ad"]
        passed = len(violations) == 0 or (len(ad_violations) == 0 and score >= 60)

        # 生成摘要
        if len(violations) == 0:
            summary = "内容检测通过"
        else:
            categories = set(v["category"] for v in violations)
            summary = f"检测到{len(violations)}处问题：{', '.join(categories)}"

        return {
            "passed": passed,
            "violations": violations,
            "summary": summary,
            "score": score,
            "ad_violations_count": len(ad_violations),
            "limit_violations_count": len([v for v in violations if v["type"] == "limit"]),
        }

    def _check_duplication(self, text: str) -> str | None:
        """检测重复内容"""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) < 3:
            return None

        # 检测连续重复行
        for i in range(len(lines) - 2):
            if lines[i] == lines[i+1] == lines[i+2]:
                return f"连续3行重复：{lines[i][:20]}..."

        # 检测短语重复
        words = text.split()
        if len(words) >= 10:
            word_freq = {}
            for i in range(len(words) - 4):
                phrase = ' '.join(words[i:i+5])
                word_freq[phrase] = word_freq.get(phrase, 0) + 1

            max_freq = max(word_freq.values()) if word_freq else 0
            if max_freq >= 5:
                for phrase, freq in word_freq.items():
                    if freq >= 5:
                        return f"短语重复：'{phrase[:20]}...' 出现{freq}次"

        return None

    def _calculate_score(self, text: str, violations: list) -> int:
        """计算内容质量分数"""
        base_score = 100

        # 基础扣分
        for v in violations:
            if v["type"] == "ad":
                base_score -= 15  # 广告词扣分更重
            elif v["type"] == "limit":
                base_score -= 10
            elif v["type"] == "style":
                base_score -= 5
            elif v["type"] == "quality":
                base_score -= 20

        # 内容长度附加分
        length = len(text)
        if length < 100:
            base_score -= 10
        elif length < 300:
            base_score -= 5
        elif 1000 <= length <= 3000:
            base_score += 5  # 适中长度加分

        return max(0, min(100, base_score))

    def suggest_fix(self, text: str, violations: list) -> dict[str, Any]:
        """
        生成修改建议

        返回: {
            "suggestions": [
                {
                    "original": str,   # 原文片段
                    "suggestion": str, # 修改建议
                    "reason": str,     # 原因
                }
            ]
        }
        """
        suggestions = []

        for v in violations:
            word = v["word"]
            pos = v["position"]

            if v["type"] == "ad":
                # 广告词替换建议
                if word in ["最", "第一", "顶级"]:
                    suggestions.append({
                        "original": f"包含'{word}'的表述",
                        "suggestion": f"改为客观描述，如'较高'、'不错'等",
                        "reason": "避免使用最高级词汇",
                    })
                elif word in ["稳赚", "保本", "零风险"]:
                    suggestions.append({
                        "original": f"'{word}'",
                        "suggestion": "删除或改为'有风险，投资需谨慎'",
                        "reason": "投资相关表述需谨慎",
                    })

            elif v["type"] == "limit":
                # 平台限流词替换建议
                suggestions.append({
                    "original": f"'{word}'",
                    "suggestion": "删除或使用同义词替代",
                    "reason": "避免平台检测限流",
                })

            elif v["type"] == "quality":
                suggestions.append({
                    "original": "重复内容段落",
                    "suggestion": "删除重复内容或进行改写",
                    "reason": "提高内容原创度",
                })

        return {"suggestions": suggestions}

    def filter_safe(self, text: str) -> str:
        """
        过滤不安全的词汇，返回安全版本

        注意：这是基础过滤，复杂情况需要人工审核
        """
        if not text:
            return text

        result = text

        # 替换明显的广告词
        for word in self.AD_WORDS[:10]:  # 只处理最常见的
            result = re.sub(re.escape(word), '*', result, flags=re.IGNORECASE)

        return result


# 全局单例
_filter: ContentFilter | None = None


def get_content_filter() -> ContentFilter:
    """获取内容过滤器单例"""
    global _filter
    if _filter is None:
        _filter = ContentFilter()
    return _filter


def check_content(text: str) -> dict[str, Any]:
    """快捷函数：检测文本内容"""
    return get_content_filter().check(text)


def suggest_fix(text: str, violations: list) -> dict[str, Any]:
    """快捷函数：生成修改建议"""
    return get_content_filter().suggest_fix(text, violations)
