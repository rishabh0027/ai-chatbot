"""
core/conversation.py
--------------------
The central orchestrator that ties every module together.
The CLI talks only to this class — it never touches LLMClient or Memory directly.

Flow for each user message:
  1.  Detect sentiment
  2.  Store user message in memory
  3.  Check if summarization is needed → summarize & inject
  4.  Build API message list with current persona
  5.  Call LLM → get reply
  6.  Store assistant reply in memory
  7.  Return reply to caller
"""

from features.persona import PersonaManager
from features.sentiment import SentimentAnalyser
from features.summarizer import Summarizer
from core.llm_client import LLMClient
from core.memory import ConversationMemory
from utils.logger import get_logger

logger = get_logger(__name__)


class Conversation:
    """
    Orchestrates a full multi-turn conversation session.

    Usage:
        conv = Conversation()
        reply = conv.send("Hello, who are you?")
        print(reply)
    """

    def __init__(self) -> None:
        self.client = LLMClient()
        self.memory = ConversationMemory()
        self.persona_manager = PersonaManager()
        self.sentiment_analyser = SentimentAnalyser(self.client)
        self.summarizer = Summarizer(self.client)

        self._last_sentiment: str = "neutral"
        logger.info("Conversation session started")

    # ── Core Method ────────────────────────────────────────────────────────

    def send(self, user_input: str) -> str:
        """
        Process a user message through the full pipeline and return the reply.

        Args:
            user_input: Raw text typed by the user.

        Returns:
            The assistant's reply string.
        """
        # 1. Sentiment analysis (non-blocking — errors are swallowed)
        try:
            self._last_sentiment = self.sentiment_analyser.analyse(user_input)
        except Exception as exc:
            logger.warning("Sentiment analysis failed: %s", exc)

        # 2. Save user message
        self.memory.add("user", user_input, sentiment=self._last_sentiment)

        # 3. Auto-summarize if history is getting long
        if self.memory.needs_summarization:
            logger.info("History threshold reached — auto-summarizing")
            try:
                summary = self.summarizer.summarize(self.memory.get_api_messages())
                self.memory.set_summary(summary)
                self.memory.clear()         # clear raw history; summary is preserved
            except Exception as exc:
                logger.warning("Auto-summarization failed: %s", exc)

        # 4. Build message list for API call
        api_messages = self.memory.get_api_messages()

        # 5. Call LLM with current persona's system prompt
        system_prompt = self.persona_manager.get_system_prompt()
        reply = self.client.chat(api_messages, system_prompt=system_prompt)

        # 6. Save assistant reply
        self.memory.add("assistant", reply)

        logger.info(
            "Turn complete | persona=%s | sentiment=%s | history_len=%d",
            self.persona_manager.current_name,
            self._last_sentiment,
            self.memory.message_count,
        )
        return reply

    # ── Utility Methods ────────────────────────────────────────────────────

    def switch_persona(self, name: str) -> bool:
        """
        Change the active persona.

        Returns:
            True if the persona exists and was switched, False otherwise.
        """
        return self.persona_manager.switch(name)

    def get_summary(self) -> str:
        """Force a one-off summary of the current conversation."""
        messages = self.memory.get_api_messages()
        if not messages:
            return "No conversation to summarize yet."
        return self.summarizer.summarize(messages)

    def clear(self) -> None:
        """Reset the conversation (keeps persona)."""
        self.memory.clear()
        logger.info("Conversation cleared by user")

    @property
    def last_sentiment(self) -> str:
        return self._last_sentiment

    @property
    def current_persona(self) -> str:
        return self.persona_manager.current_name

    @property
    def available_personas(self) -> list[str]:
        return self.persona_manager.list_personas()
