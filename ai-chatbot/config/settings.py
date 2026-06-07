"""
config/settings.py
------------------
Centralized configuration loaded from environment variables.
All modules import from here — never hardcode values elsewhere.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file


class Settings:
    """Application-wide settings loaded from environment variables."""

    # ── API ────────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL_NAME: str = "claude-sonnet-4-20250514"
    MAX_TOKENS: int = 1024

    # ── Conversation ───────────────────────────────────────────────────────
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
    # When history exceeds this, auto-summarization kicks in
    SUMMARIZE_THRESHOLD: int = 15
    DEFAULT_PERSONA: str = os.getenv("DEFAULT_PERSONA", "assistant")

    # ── App ────────────────────────────────────────────────────────────────
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    APP_VERSION: str = "1.0.0"

    # ── Paths ──────────────────────────────────────────────────────────────
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXPORTS_DIR: str = os.path.join(BASE_DIR, "exports")
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")

    def validate(self) -> None:
        """Raise an error early if critical config is missing."""
        if not self.ANTHROPIC_API_KEY:
            raise ValueError(
                "❌ ANTHROPIC_API_KEY is not set.\n"
                "   Copy .env.example → .env and add your API key."
            )


# Singleton instance — import this everywhere
settings = Settings()
