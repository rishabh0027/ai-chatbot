"""
features/sentiment.py
---------------------
Lightweight sentiment analysis using the LLM itself.
No external ML libraries needed — the model classifies user intent in one call.

Returns one of: positive | negative | neutral | frustrated | curious | excited
"""

from core.llm_client import LLMClient
from utils.logger import get_logger

logger = get_logger(__name__)

SENTIMENT_SYSTEM = (
    "You are a sentiment classifier. "
    "Given a user message, respond with EXACTLY ONE word from this list: "
    "positive, negative, neutral, frustrated, curious, excited. "
    "No explanation. No punctuation. Just the single word."
)

VALID_SENTIMENTS = {"positive", "negative", "neutral", "frustrated", "curious", "excited"}

# Emoji map for display in the CLI
SENTIMENT_EMOJI: dict[str, str] = {
    "positive":   "😊",
    "negative":   "😞",
    "neutral":    "😐",
    "frustrated": "😤",
    "curious":    "🤔",
    "excited":    "🤩",
}


class SentimentAnalyser:
    """
    Analyses the emotional tone of a user message.

    Uses a constrained LLM prompt for classification.
    Falls back to "neutral" if the response is unexpected.
    """

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def analyse(self, text: str) -> str:
        """
        Classify the sentiment of the given text.

        Args:
            text: The user's message.

        Returns:
            A sentiment label string.
        """
        if not text.strip():
            return "neutral"

        raw = self._client.simple_prompt(
            prompt=f"Message: {text}",
            system=SENTIMENT_SYSTEM,
        )

        sentiment = raw.strip().lower().rstrip(".")
        if sentiment not in VALID_SENTIMENTS:
            logger.warning("Unexpected sentiment value '%s' — defaulting to neutral", sentiment)
            sentiment = "neutral"

        logger.debug("Sentiment for message: %s", sentiment)
        return sentiment

    @staticmethod
    def get_emoji(sentiment: str) -> str:
        """Return a display emoji for a given sentiment label."""
        return SENTIMENT_EMOJI.get(sentiment, "😐")
