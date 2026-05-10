"""
Centralized logging.

Why loguru over stdlib logging:
    - Zero-config structured output
    - Automatic file rotation
    - Colored console
    - Test-friendly (easy to capture/redirect per worker)

Usage anywhere in the framework:
    from src.core.logger import logger
    logger.info("Starting login flow for user=%s", user)
"""
from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path("reports/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Reset default handler so we control format precisely
logger.remove()

# Console — concise, colored
logger.add(
    sys.stdout,
    level="INFO",
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    colorize=True,
    backtrace=False,
    diagnose=False,
)

# File — verbose, rotated, retained 7 days
logger.add(
    LOG_DIR / "framework_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    rotation="50 MB",
    retention="7 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    enqueue=True,            # safe under pytest-xdist parallel workers
    backtrace=True,
    diagnose=False,          # keep secrets out of logs
)

__all__ = ["logger"]
