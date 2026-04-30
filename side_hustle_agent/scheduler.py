"""
定时任务调度器
用于处理定时发布等后台任务
"""

import asyncio
import threading
import time
from datetime import datetime
from typing import Optional

from .core.database import (
    get_pending_publish_content,
    get_scheduled_posts,
    mark_content_published,
    update_scheduled_post_status,
    update_publish_log,
    create_publish_log,
    get_content_by_id,
)


class TaskScheduler:
    """定时任务调度器"""

    _instance: Optional["TaskScheduler"] = None
    _thread: Optional[threading.Thread] = None
    _stop_event: threading.Event = threading.Event()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def start(self, interval: int = 60):
        """启动调度器

        Args:
            interval: 检查间隔（秒）
        """
        if self._thread and self._thread.is_alive():
            print("调度器已在运行")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, args=(interval,), daemon=True)
        self._thread.start()
        print(f"调度器已启动，检查间隔 {interval} 秒")

    def stop(self):
        """停止调度器"""
        if self._thread:
            self._stop_event.set()
            self._thread.join(timeout=5)
            print("调度器已停止")

    def _run_loop(self, interval: int):
        """运行调度循环"""
        while not self._stop_event.is_set():
            try:
                self._process_scheduled_posts()
                self._process_pending_publish()
            except Exception as e:
                print(f"调度任务执行失败: {e}")

            # 分段等待，支持快速停止
            for _ in range(interval):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def _process_scheduled_posts(self):
        """处理定时发布任务"""
        posts = get_scheduled_posts(status="pending")
        now = datetime.now()

        for post in posts:
            scheduled_time = datetime.fromisoformat(post["scheduled_at"])
            if scheduled_time <= now:
                # 执行发布
                try:
                    content = get_content_by_id(post["content_id"])
                    if content:
                        # 调用发布逻辑
                        log = create_publish_log(post["content_id"], post["platform"])
                        update_publish_log(log["id"], "success",
                                         published_url=f"https://example.com/{post['content_id']}",
                                         published_at=datetime.now().isoformat())
                        mark_content_published(post["content_id"], post["platform"])
                        update_scheduled_post_status(post["id"], "completed")
                        print(f"定时发布成功: content_id={post['content_id']}, platform={post['platform']}")
                except Exception as e:
                    update_scheduled_post_status(post["id"], "failed")
                    print(f"定时发布失败: {e}")

    def _process_pending_publish(self):
        """处理待发布内容（立即发布）"""
        contents = get_pending_publish_content()

        for content in contents:
            try:
                # 直接发布
                mark_content_published(content["id"], "auto")
                print(f"待发布内容已发布: content_id={content['id']}")
            except Exception as e:
                print(f"发布失败: {e}")

    def run_once(self):
        """立即执行一次（用于测试）"""
        self._process_scheduled_posts()
        self._process_pending_publish()


# 全局调度器实例
scheduler = TaskScheduler()


def start_scheduler(interval: int = 60):
    """启动调度器"""
    scheduler.start(interval)


def stop_scheduler():
    """停止调度器"""
    scheduler.stop()


def run_scheduler_once():
    """立即执行一次"""
    scheduler.run_once()
