"""
core/llm_client.py
------------------
Low-level wrapper around the Anthropic Python SDK.
All direct API calls live here — other modules never touch the SDK directly.
This design makes it trivial to swap out the LLM provider later.
"""

from typing import Optional
import anthropic

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """
    Wraps the Anthropic Claude API.

    Responsibilities:
    - Initialise the SDK client once
    - Send messages and return the response text
    - Handle and log API errors gracefully
    """

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        logger.info("LLMClient initialised (model=%s)", settings.MODEL_NAME)

    def chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
        max_tokens: int = settings.MAX_TOKENS,
        temperature: float = 0.7,
    ) -> str:
        """
        Send a list of messages to the LLM and return the assistant's reply.

        Args:
            messages:      List of {"role": "user"|"assistant", "content": str}
            system_prompt: Optional system-level instruction for the model
            max_tokens:    Maximum tokens in the response
            temperature:   Creativity (0 = deterministic, 1 = creative)

        Returns:
            The assistant's reply as a plain string.

        Raises:
            RuntimeError: On any API-level failure.
        """
        try:
            kwargs: dict = {
                "model": settings.MODEL_NAME,
                "max_tokens": max_tokens,
                "messages": messages,
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            logger.debug("Sending %d message(s) to LLM", len(messages))
            response = self._client.messages.create(**kwargs)

            reply: str = response.content[0].text
            logger.debug("Received reply (%d chars)", len(reply))
            return reply

        except anthropic.AuthenticationError:
            msg = "Invalid API key. Check your ANTHROPIC_API_KEY in .env"
            logger.error(msg)
            raise RuntimeError(msg)

        except anthropic.RateLimitError:
            msg = "Rate limit hit. Please wait a moment before trying again."
            logger.warning(msg)
            raise RuntimeError(msg)

        except anthropic.APIConnectionError as exc:
            msg = f"Network error connecting to Anthropic API: {exc}"
            logger.error(msg)
            raise RuntimeError(msg)

        except anthropic.APIError as exc:
            msg = f"Unexpected API error: {exc}"
            logger.error(msg)
            raise RuntimeError(msg)

    def simple_prompt(self, prompt: str, system: str = "") -> str:
        """
        Convenience method for a single one-shot prompt (no history).

        Args:
            prompt: The user's message
            system: Optional system instruction

        Returns:
            The model's reply as a string.
        """
        return self.chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system,
        )
