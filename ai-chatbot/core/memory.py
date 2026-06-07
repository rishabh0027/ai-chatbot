"""
core/memory.py
--------------
Manages the rolling window of conversation messages.
Keeps history within MAX_HISTORY_MESSAGES to avoid exceeding token limits.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Message:
    """A single conversation message with metadata."""
    role: str          # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    sentiment: Optional[str] = None   # filled in by SentimentAnalyser


class ConversationMemory:
    """
    Stores and manages the conversation history.

    Features:
    - Enforces a sliding window (MAX_HISTORY_MESSAGES)
    - Exposes history in the exact format the Anthropic SDK expects
    - Supports injection of a summary message when history is trimmed
    """

    def __init__(self, max_messages: int = settings.MAX_HISTORY_MESSAGES) -> None:
        self._messages: list[Message] = []
        self.max_messages = max_messages
        self._summary: Optional[str] = None  # set by Summarizer when trimming

    # ── Public API ─────────────────────────────────────────────────────────

    def add(self, role: str, content: str, sentiment: Optional[str] = None) -> None:
        """Append a new message and trim if over the limit."""
        msg = Message(role=role, content=content, sentiment=sentiment)
        self._messages.append(msg)
        logger.debug("Memory: added [%s] message. Total=%d", role, len(self._messages))
        self._enforce_limit()

    def get_api_messages(self) -> list[dict]:
        """
        Return messages in Anthropic API format:
        [{"role": "user", "content": "..."}, ...]

        If a summary exists, it's prepended as a special assistant note.
        """
        api_msgs: list[dict] = []

        if self._summary:
            # Inject summary as a user→assistant pair so the model has context
            api_msgs.append({
                "role": "user",
                "content": "[System: Here is a summary of our earlier conversation]"
            })
            api_msgs.append({
                "role": "assistant",
                "content": self._summary
            })

        for msg in self._messages:
            api_msgs.append({"role": msg.role, "content": msg.content})

        return api_msgs

    def get_all(self) -> list[Message]:
        """Return raw Message objects (used for export, display, etc.)."""
        return list(self._messages)

    def set_summary(self, summary: str) -> None:
        """Store a summary produced by the Summarizer."""
        self._summary = summary
        logger.info("Memory: conversation summary stored (%d chars)", len(summary))

    def clear(self) -> None:
        """Wipe all history and any stored summary."""
        self._messages.clear()
        self._summary = None
        logger.info("Memory: cleared")

    @property
    def message_count(self) -> int:
        return len(self._messages)

    @property
    def needs_summarization(self) -> bool:
        return len(self._messages) >= settings.SUMMARIZE_THRESHOLD

    # ── Private ────────────────────────────────────────────────────────────

    def _enforce_limit(self) -> None:
        """Drop oldest messages when the window is exceeded."""
        if len(self._messages) > self.max_messages:
            dropped = len(self._messages) - self.max_messages
            self._messages = self._messages[dropped:]
            logger.debug("Memory: trimmed %d old message(s)", dropped)
