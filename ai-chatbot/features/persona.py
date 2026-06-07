"""
features/persona.py
-------------------
Defines multiple chatbot personas, each with a different system prompt.
Switching persona changes the bot's entire tone, expertise, and style.

Adding a new persona: just add an entry to PERSONAS below.
"""

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Persona Definitions ────────────────────────────────────────────────────────
#
# Each persona has:
#   name        - display name
#   system      - the system prompt sent to the LLM
#   description - shown in /help
#
PERSONAS: dict[str, dict] = {
    "assistant": {
        "name": "Assistant",
        "description": "General-purpose helpful AI",
        "system": (
            "You are a knowledgeable, friendly, and concise AI assistant. "
            "Answer questions clearly and accurately. When unsure, say so. "
            "Keep responses focused and avoid unnecessary padding."
        ),
    },
    "teacher": {
        "name": "Teacher",
        "description": "Explains concepts from first principles",
        "system": (
            "You are a patient and enthusiastic teacher. Your goal is to explain "
            "concepts clearly, using simple language, real-world analogies, and "
            "step-by-step reasoning. Always check for understanding by asking "
            "a follow-up question at the end of your explanation."
        ),
    },
    "debugger": {
        "name": "Debugger",
        "description": "Expert code reviewer and bug fixer",
        "system": (
            "You are a senior software engineer specialising in debugging and code review. "
            "When given code or an error, methodically identify the root cause, explain "
            "why it is a problem, and provide a corrected version with comments. "
            "Always consider edge cases and suggest best practices."
        ),
    },
    "chef": {
        "name": "Chef",
        "description": "Culinary expert and recipe advisor",
        "system": (
            "You are a world-class chef with expertise in cuisines from around the globe. "
            "You provide detailed recipes, cooking tips, ingredient substitutions, and "
            "plating suggestions. Be enthusiastic about food and always mention one "
            "pro tip per response."
        ),
    },
    "socratic": {
        "name": "Socratic",
        "description": "Guides learning through questions",
        "system": (
            "You are a Socratic tutor. Instead of giving direct answers, you guide the user "
            "to discover answers themselves through thoughtful questions. Only reveal the "
            "answer after the user has made a genuine attempt. Praise effort, not just correctness."
        ),
    },
}


class PersonaManager:
    """Manages the active persona and exposes its system prompt."""

    def __init__(self, default: str = settings.DEFAULT_PERSONA) -> None:
        self._current_key: str = default if default in PERSONAS else "assistant"
        logger.info("PersonaManager initialised with persona='%s'", self._current_key)

    def switch(self, name: str) -> bool:
        """
        Switch to a different persona by key name.

        Args:
            name: Persona key (e.g. "teacher")

        Returns:
            True if successful, False if persona not found.
        """
        key = name.lower().strip()
        if key not in PERSONAS:
            logger.warning("Persona '%s' not found", key)
            return False
        self._current_key = key
        logger.info("Switched to persona '%s'", key)
        return True

    def get_system_prompt(self) -> str:
        """Return the system prompt for the currently active persona."""
        return PERSONAS[self._current_key]["system"]

    def list_personas(self) -> list[str]:
        """Return all available persona keys."""
        return list(PERSONAS.keys())

    def get_persona_info(self) -> dict:
        """Return full info dict for the current persona."""
        return PERSONAS[self._current_key]

    @property
    def current_name(self) -> str:
        return PERSONAS[self._current_key]["name"]
