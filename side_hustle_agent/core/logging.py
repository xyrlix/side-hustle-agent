"""
日志配置
"""

import logging
import sys
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化"""

    COLORS = {
        "DEBUG": "\033[36m",    # 青色
        "INFO": "\033[32m",     # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",    # 红色
        "CRITICAL": "\033[35m", # 紫色
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """设置日志"""
    logger = logging.getLogger("side_hustle_agent")
    logger.setLevel(getattr(logging, level.upper()))

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # 格式化
    formatter = ColoredFormatter(
        "%(asctime)s │ %(levelname)s │ %(name)s ─ %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


# 全局日志实例
logger = setup_logging()