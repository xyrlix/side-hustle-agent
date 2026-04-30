"""
mmx-cli 本地 AI 能力封装

提供对 mmx-cli 命令行工具的调用封装，支持：
- 文本生成
- 图像生成/处理
- 视频处理
- 语音处理
- 搜索
"""

import subprocess
import json
import os
import re
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class MMxResult:
    """mmx-cli 调用结果"""
    success: bool
    content: Any
    error: str | None = None
    raw_output: str | None = None


class MMxClient:
    """mmx-cli 客户端封装"""

    def __init__(self, mmx_path: str | None = None):
        """
        初始化 mmx-cli 客户端

        mmx_path: mmx-cli 可执行文件路径，默认从 PATH 或常见位置查找
        """
        self.mmx_path = mmx_path or self._find_mmx()

    def _find_mmx(self) -> Optional[str]:
        """查找 mmx-cli 可执行文件"""
        # 检查环境变量
        env_path = os.environ.get("MMX_CLI_PATH")
        if env_path and os.path.exists(env_path):
            return env_path

        # 检查常见位置
        common_paths = [
            "mmx-cli",
            "C:\\Program Files\\mmx-cli\\mmx-cli.exe",
            "C:\\Users\\UDing\\.local\\bin\\mmx-cli",
            os.path.expanduser("~/.local/bin/mmx-cli"),
        ]

        for path in common_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue

        # 尝试直接调用（PATH 中）
        try:
            result = subprocess.run(["mmx-cli", "--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return "mmx-cli"
        except:
            pass

        return None

    def _run_command(self, args: list[str], input_text: str | None = None, timeout: int = 120) -> MMxResult:
        """执行 mmx-cli 命令"""
        if not self.mmx_path:
            return MMxResult(
                success=False,
                content=None,
                error="mmx-cli 未找到，请确保已安装并配置在 PATH 中",
            )

        try:
            cmd = [self.mmx_path] + args
            result = subprocess.run(
                cmd,
                input=input_text.encode() if input_text else None,
                capture_output=True,
                text=False,
                timeout=timeout,
            )

            if result.returncode == 0:
                return MMxResult(
                    success=True,
                    content=result.stdout.decode("utf-8", errors="ignore"),
                    raw_output=result.stdout.decode("utf-8", errors="ignore"),
                )
            else:
                return MMxResult(
                    success=False,
                    content=None,
                    error=result.stderr.decode("utf-8", errors="ignore") or f"命令执行失败 (code {result.returncode})",
                    raw_output=result.stdout.decode("utf-8", errors="ignore"),
                )
        except subprocess.TimeoutExpired:
            return MMxResult(success=False, content=None, error=f"命令执行超时 ({timeout}s)")
        except Exception as e:
            return MMxResult(success=False, content=None, error=str(e))

    def generate_text(self, prompt: str, model: str = "default", **kwargs) -> MMxResult:
        """
        生成文本

        args:
            prompt: 提示词
            model: 模型选择
            **kwargs: 其他参数（如 temperature, max_tokens 等）
        """
        args = ["text", "--prompt", prompt, "--model", model]
        return self._run_command(args)

    def generate_image(self, prompt: str, output: str | None = None, **kwargs) -> MMxResult:
        """
        生成图像

        args:
            prompt: 图像描述
            output: 输出路径
            **kwargs: 其他参数（如尺寸、风格等）
        """
        args = ["image", "--prompt", prompt]
        if output:
            args.extend(["--output", output])
        return self._run_command(args)

    def process_video(self, input_path: str, operation: str, **kwargs) -> MMxResult:
        """
        处理视频

        args:
            input_path: 输入视频路径
            operation: 操作类型（如 "cut", "merge", "subtitle"）
            **kwargs: 其他参数
        """
        args = ["video", operation, "--input", input_path]
        return self._run_command(args)

    def process_audio(self, input_path: str, operation: str, **kwargs) -> MMxResult:
        """
        处理音频

        args:
            input_path: 输入音频路径
            operation: 操作类型（如 "transcribe", "voiceover"）
            **kwargs: 其他参数
        """
        args = ["audio", operation, "--input", input_path]
        return self._run_command(args)

    def search(self, query: str, source: str = "web", **kwargs) -> MMxResult:
        """
        搜索

        args:
            query: 搜索查询
            source: 搜索来源（如 "web", "news"）
        """
        args = ["search", "--query", query, "--source", source]
        return self._run_command(args)

    def is_available(self) -> bool:
        """检查 mmx-cli 是否可用"""
        return self._find_mmx() is not None


class ContentCreator:
    """内容创作助手 - 基于 mmx-cli 的能力"""

    def __init__(self, mmx_client: MMxClient | None = None):
        self.mmx = mmx_client or MMxClient()
        self._llm_fallback: Optional[Any] = None  # 备用 LLM

    def set_llm_fallback(self, llm_provider):
        """设置 LLM 备用（当 mmx-cli 不可用时）"""
        self._llm_fallback = llm_provider

    async def generate_content(self, topic: str, platform: str, style: str = "专业") -> dict[str, Any]:
        """
        生成内容

        args:
            topic: 主题
            platform: 目标平台
            style: 风格

        返回:
            {
                "title": str,
                "body": str,
                "tags": list[str],
            }
        """
        # 构建提示词
        prompt = self._build_content_prompt(topic, platform, style)

        # 尝试使用 mmx-cli
        if self.mmx.is_available():
            result = self.mmx.generate_text(prompt)
            if result.success:
                return self._parse_content(result.content, platform)
            # 如果 mmx 失败，尝试 LLM 备用
            if self._llm_fallback:
                try:
                    response = await self._llm_fallback.chat(messages=[{"role": "user", "content": prompt}])
                    return self._parse_content(response.content, platform)
                except:
                    pass

        # 最后尝试纯 LLM（如果配置了）
        if self._llm_fallback:
            try:
                response = await self._llm_fallback.chat(messages=[{"role": "user", "content": prompt}])
                return self._parse_content(response.content, platform)
            except Exception as e:
                return {"success": False, "error": str(e)}

        return {"success": False, "error": "无可用的文本生成工具"}

    def _build_content_prompt(self, topic: str, platform: str, style: str) -> str:
        """构建内容生成提示词"""
        platform_hints = {
            "wechat_public": "请生成一篇公众号深度文章，包括吸引人的标题和1500-3000字的正文内容。",
            "toutiao": "请生成一篇头条号爆款文章，标题要有悬念，正文800-1500字，节奏快。",
            "xiaohongshu": "请生成一篇小红书种草笔记，标题用emoji，正文精简有干货，500-800字。",
            "zhihu": "请生成一篇知乎回答，专业有深度，1000-2000字。",
        }
        hint = platform_hints.get(platform, "请生成一篇适合的内容。")
        return f"主题：{topic}\n风格：{style}\n{hint}\n\n请直接输出内容，不要额外解释。"

    def _parse_content(self, raw: str, platform: str) -> dict[str, Any]:
        """解析生成的内容"""
        title = ""
        body = ""
        tags = []

        lines = raw.strip().split("\n")
        title_found = False

        for line in lines:
            if not title_found and line.strip() and len(line.strip()) < 50:
                title = line.strip()
                title_found = True
            elif title_found:
                if line.strip():
                    body += line + "\n"

        body = body.strip()

        # 提取标签
        if "#" in raw:
            tag_match = re.search(r'#(\w+)', raw)
            if tag_match:
                tags = re.findall(r'#(\w+)', raw)

        return {
            "success": True,
            "title": title or "未命名",
            "body": body or raw,
            "tags": tags,
        }

    def search_trends(self, keywords: list[str], limit: int = 5) -> list[dict[str, Any]]:
        """
        搜索热点话题

        返回: [{"keyword": str, "trend": str, "related": list}]
        """
        if not self.mmx.is_available():
            return []

        results = []
        for keyword in keywords[:limit]:
            result = self.mmx.search(keyword, source="news")
            if result.success:
                try:
                    # 尝试解析 JSON 输出
                    data = json.loads(result.content)
                    results.append({"keyword": keyword, "data": data})
                except:
                    results.append({"keyword": keyword, "raw": result.content})

        return results


# 便捷函数
_mmx_client: MMxClient | None = None


def get_mmx_client() -> MMxClient:
    """获取全局 mmx-cli 客户端"""
    global _mmx_client
    if _mmx_client is None:
        _mmx_client = MMxClient()
    return _mmx_client


def is_mmx_available() -> bool:
    """检查 mmx-cli 是否可用"""
    return get_mmx_client().is_available()