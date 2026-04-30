"""
内容创作 Agent

使用 LLM 生成各平台适配的内容，支持公众号、头条号、小红书等平台。
"""

import json
from typing import Any

from .base import BaseAgent
from ..core.memory import get_memory
from ..core.models import Content


# 平台内容格式提示
PLATFORM_PROMPTS = {
    "wechat_public": """你是一位资深公众号编辑，擅长撰写深度文章。
要求：
- 标题吸引人且有传播性
- 文章结构：开篇引入 + 3-5个核心观点 + 总结升华
- 语言风格：专业但不晦涩，善用讲故事的方式
- 字数要求：1500-3000字
- 可以加入小标题增强可读性

输出格式：
【标题】
【正文】""",

    "toutiao": """你是一位头条号内容创作者，擅长撰写高点击量的爆款文章。
要求：
- 标题要制造悬念或冲突，引发好奇
- 文章节奏快，信息密度高
- 善用数据和案例支撑观点
- 语言口语化，通俗易懂
- 字数要求：800-2000字
- 开头就要抓住读者

输出格式：
【标题】
【正文】""",

    "xiaohongshu": """你是一位小红书博主，擅长撰写种草笔记和生活方式内容。
要求：
- 标题要有情绪感和代入感，善用emoji
- 正文字数精简，每段不超过3行
- 善用标签和话题增加曝光
- 内容要有实用价值，干货满满
- 格式：攻略/测评/种草/避坑类
- 字数要求：500-1000字
- 结尾要有互动引导（收藏、点赞）

输出格式：
【标题】
【正文】
【标签】""",

    "zhihu": """你是一位知乎专业回答者，擅长撰写有深度的专业内容。
要求：
- 回答要有理有据，逻辑严密
- 善用专业术语但解释清楚
- 可以引用数据和案例
- 结构：问题定义 + 分析 + 解决方案 + 总结
- 字数要求：1000-3000字
- 结尾可以有延伸阅读建议

输出格式：
【回答】""",

    "default": """你是一位内容创作者，擅长撰写各类平台适用的优质内容。
要求：
- 标题吸引人
- 内容有价值、有干货
- 结构清晰
- 语言流畅

输出格式：
【标题】
【正文】"""
}


class ContentGeneratorAgent(BaseAgent):
    """内容创作 Agent"""

    def __init__(self, memory=None):
        super().__init__("ContentGenerator", memory)
        self.platform_prompts = PLATFORM_PROMPTS

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        生成内容

        input_data: {
            "topic": str,           # 主题
            "platform": str,         # 目标平台
            "style": str,            # 风格偏好
            "keywords": list[str],   # 关键词
            "length": str,           # 长度偏好
        }

        返回: {
            "success": bool,
            "content": {
                "title": str,
                "body": str,
                "tags": list[str],
                "platform": str,
            },
            "platform_versions": dict[str, str],  # 其他平台适配版本
        }
        """
        topic = input_data.get("topic", "")
        platform = input_data.get("platform", "default")
        style = input_data.get("style", "专业")
        keywords = input_data.get("keywords", [])
        length = input_data.get("length", "中等")

        if not topic:
            return {"success": False, "error": "主题不能为空"}

        # 构建生成提示词
        platform_hint = self.platform_prompts.get(platform, self.platform_prompts["default"])

        length_hint = {
            "短": "字数控制在500-800字",
            "中等": "字数控制在1000-1500字",
            "长": "字数控制在2000-3000字"
        }.get(length, "字数控制在1000-1500字")

        keyword_hint = f"核心关键词：{', '.join(keywords)}" if keywords else ""

        prompt = f"""请根据以下主题生成{platform}平台的内容：

主题：{topic}
风格：{style}
{length_hint}
{keyword_hint}

{platform_hint}

请生成完整的内容，包括标题和正文。"""

        try:
            result = await self.think(prompt)
            content = self._parse_content(result, platform)

            # 生成其他平台的适配版本
            platform_versions = {}
            other_platforms = [p for p in self.platform_prompts.keys() if p != platform and p != "default"]
            for other_platform in other_platforms[:2]:  # 只生成2个额外版本
                other_hint = ""
                other_prompt_template = self.platform_prompts.get(other_platform, "")
                if "要求：" in other_prompt_template:
                    parts = other_prompt_template.split("要求：")
                    if len(parts) > 1:
                        hint_part = parts[1].split("\n")[0]
                        other_hint = f" - {hint_part}"

                version_prompt = f"""将以下内容改写成{other_platform}平台的版本：

原文：
{content['body']}

要求：
- 保持核心信息不变
- 调整格式和风格以适应平台特点
{other_hint}

直接输出改写后的内容，不要额外解释。"""

                try:
                    version_result = await self.think(version_prompt)
                    platform_versions[other_platform] = version_result
                except:
                    pass

            return {
                "success": True,
                "content": {
                    "title": content["title"],
                    "body": content["body"],
                    "tags": content.get("tags", []),
                    "platform": platform,
                },
                "platform_versions": platform_versions,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_content(self, result: str, platform: str) -> dict[str, Any]:
        """解析 LLM 返回的内容"""
        title = ""
        body = ""
        tags = []

        lines = result.strip().split("\n")
        in_body = False
        body_lines = []

        for line in lines:
            if line.startswith("【标题】"):
                title = line.replace("【标题】", "").strip()
            elif line.startswith("【正文】"):
                in_body = True
                continue
            elif line.startswith("【回答】"):
                in_body = True
                continue
            elif line.startswith("【标签】"):
                tag_line = line.replace("【标签】", "").strip()
                tags = [t.strip() for t in tag_line.split("#") if t.strip()]
            elif in_body:
                body_lines.append(line)

        body = "\n".join(body_lines).strip()

        # 如果没有解析到标题，尝试从第一行获取
        if not title and lines:
            for line in lines[:5]:
                if len(line.strip()) > 5 and len(line.strip()) < 50:
                    title = line.strip()
                    break

        return {"title": title, "body": body, "tags": tags}

    async def generate_with_prompt(self, base_prompt: str, context: dict[str, Any] = None) -> str:
        """
        使用自定义提示词生成内容

        base_prompt: 基础提示词模板
        context: 上下文变量
        """
        prompt = base_prompt
        if context:
            for key, value in context.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))

        return await self.think(prompt)


class ContentAdaptor:
    """内容适配器 - 将一篇内容适配到不同平台"""

    def __init__(self, agent: ContentGeneratorAgent):
        self.agent = agent

    async def adapt(self, content: Content, target_platforms: list[str]) -> dict[str, str]:
        """
        将已有内容适配到多个平台

        content: Content 对象
        target_platforms: 目标平台列表

        返回: {platform: adapted_content}
        """
        versions = {}

        for platform in target_platforms:
            if platform == "wechat_public":
                # 公众号：扩展为深度文章
                prompt = f"""将以下内容扩展为一篇公众号风格的深度文章：

原文：
{content.body}

要求：
- 保持核心观点不变
- 扩展为1500-3000字的深度内容
- 增加案例和故事增强可读性
- 使用小标题划分章节

直接输出扩展后的内容。"""
            elif platform == "toutiao":
                # 头条号：调整为爆款风格
                prompt = f"""将以下内容改写为头条号风格的爆款文章：

原文：
{content.body}

要求：
- 标题制造悬念或冲突
- 开头就要抓住读者
- 节奏快，信息密度高
- 语言口语化
- 字数800-1500字

直接输出改写后的内容。"""
            elif platform == "xiaohongshu":
                # 小红书：精简种草风格
                requirement = self.platform_prompts.get("xiaohongshu", "").split("要求：")[1].split("\n")[0] if "要求：" in self.platform_prompts.get("xiaohongshu", "") else ""
                prompt = f"""将以下内容改写为小红书风格的种草笔记：

原文：
{content.body}

要求：
- 标题要有情绪感，善用emoji
- 每段不超过3行
- 加入实用干货
- 结尾引导互动
- 字数500-800字

直接输出改写后的内容。"""
            else:
                continue

            try:
                result = await self.agent.think(prompt)
                versions[platform] = result
            except:
                pass

        return versions