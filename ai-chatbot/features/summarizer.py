"""
features/summarizer.py
----------------------
Compresses a long conversation into a concise summary.

Used in two ways:
  1. Auto-triggered by Conversation when history hits the SUMMARIZE_THRESHOLD
  2. Manually triggered by the user with /summary command
"""

from core.llm_client import LLMClient
from utils.logger import get_logger

logger = get_logger(__name__)

SUMMARIZER_SYSTEM = (
    "You are a concise conversation summarizer. "
    "Given a conversation history, produce a clear, structured summary that captures: "
    "1) The main topics discussed, "
    "2) Key decisions or conclusions reached, "
    "3) Any important context the assistant should remember going forward. "
    "Be brief but comprehensive. Use bullet points."
)


class Summarizer:
    """
    Generates a concise summary of a conversation history.

    The summary is stored in ConversationMemory and prepended to future
    API calls so the model retains context after the raw history is trimmed.
    """

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def summarize(self, messages: list[dict]) -> str:
        """
        Summarize a list of conversation messages.

        Args:
            messages: Conversation history in Anthropic API format.

        Returns:
            A plain-text summary string.
        """
        if not messages:
            return "No conversation history to summarize."

        # Format the conversation for the summarizer
        formatted_convo = self._format_messages(messages)

        prompt = f"Please summarize the following conversation:\n\n{formatted_convo}"

        summary = self._client.simple_prompt(
            prompt=prompt,
            system=SUMMARIZER_SYSTEM,
        )

        logger.info(
            "Summarized %d messages into %d-char summary",
            len(messages),
            len(summary),
        )
        return summary

    @staticmethod
    def _format_messages(messages: list[dict]) -> str:
        """Convert API-format messages into a readable transcript."""
        lines: list[str] = []
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
