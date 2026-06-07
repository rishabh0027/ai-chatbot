"""
utils/helpers.py
----------------
Shared utility functions used across multiple modules.
Keep this file small — if a helper grows complex, move it to its own module.
"""

import json
import os
from datetime import datetime
from typing import Any

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def timestamp_filename(prefix: str, extension: str) -> str:
    """
    Generate a timestamped filename.

    Example:
        timestamp_filename("chat", "json") → "chat_2024-01-15_10-30-45.json"
    """
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}_{ts}.{extension}"


def ensure_dir(path: str) -> None:
    """Create a directory (and parents) if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def export_conversation_json(messages: list, persona: str) -> str:
    """
    Save conversation history to a JSON file in the exports directory.

    Args:
        messages: List of Message objects from ConversationMemory.
        persona:  Name of the active persona.

    Returns:
        The full path to the saved file.
    """
    ensure_dir(settings.EXPORTS_DIR)
    filename = timestamp_filename("chat", "json")
    filepath = os.path.join(settings.EXPORTS_DIR, filename)

    payload: dict[str, Any] = {
        "exported_at": datetime.now().isoformat(),
        "persona": persona,
        "message_count": len(messages),
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "sentiment": msg.sentiment,
            }
            for msg in messages
        ],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    logger.info("Exported conversation to %s", filepath)
    return filepath


def export_conversation_txt(messages: list, persona: str) -> str:
    """
    Save conversation history to a plain text file.

    Returns:
        The full path to the saved file.
    """
    ensure_dir(settings.EXPORTS_DIR)
    filename = timestamp_filename("chat", "txt")
    filepath = os.path.join(settings.EXPORTS_DIR, filename)

    lines: list[str] = [
        f"AI Chatbot — Conversation Export",
        f"Exported : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Persona  : {persona}",
        f"Messages : {len(messages)}",
        "=" * 60,
        "",
    ]

    for msg in messages:
        label = "You" if msg.role == "user" else "🤖 Bot"
        sentiment_tag = f" [{msg.sentiment}]" if msg.sentiment else ""
        lines.append(f"{label}{sentiment_tag}:")
        lines.append(msg.content)
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("Exported conversation to %s", filepath)
    return filepath


def word_count(text: str) -> int:
    """Count words in a string."""
    return len(text.split())


def truncate(text: str, max_chars: int = 80) -> str:
    """Truncate a string to max_chars with ellipsis."""
    return text if len(text) <= max_chars else text[:max_chars - 3] + "..."
