"""
utils/logger.py
---------------
Configures a rotating file logger + console logger.
Every module calls get_logger(__name__) to get its own named logger.

Logs are written to logs/chatbot.log with automatic rotation at 5 MB.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from config.settings import settings

# Ensure the logs directory exists
os.makedirs(settings.LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(settings.LOGS_DIR, "chatbot.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False  # Guard against double-configuration


def _configure_root_logger() -> None:
    global _configured
    if _configured:
        return

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # ── File handler (rotating, max 5 MB, keep 3 backups) ─────────────────
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # ── Console handler (WARNING and above only — don't clutter the UI) ───
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    root.addHandler(file_handler)
    root.addHandler(console_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a module.

    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Module initialised")
    """
    _configure_root_logger()
    return logging.getLogger(name)
