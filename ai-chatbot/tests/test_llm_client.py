"""
tests/test_llm_client.py
------------------------
Unit tests for LLMClient.
Mocks the anthropic SDK so no real API calls are made.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLLMClient(unittest.TestCase):
    """Tests for the LLMClient wrapper."""

    def _make_client(self):
        """Create an LLMClient with the Anthropic SDK fully mocked."""
        with patch("core.llm_client.anthropic.Anthropic") as MockAnthropic:
            # Mock the response object
            mock_content = MagicMock()
            mock_content.text = "This is a mocked response."

            mock_response = MagicMock()
            mock_response.content = [mock_content]

            mock_sdk = MockAnthropic.return_value
            mock_sdk.messages.create.return_value = mock_response

            from core.llm_client import LLMClient
            client = LLMClient()
            client._client = mock_sdk
            return client, mock_sdk

    def test_chat_returns_string(self):
        client, _ = self._make_client()
        messages = [{"role": "user", "content": "Hello"}]
        result = client.chat(messages)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "This is a mocked response.")

    def test_chat_passes_messages_to_sdk(self):
        client, mock_sdk = self._make_client()
        messages = [{"role": "user", "content": "Test message"}]
        client.chat(messages)
        mock_sdk.messages.create.assert_called_once()
        call_kwargs = mock_sdk.messages.create.call_args.kwargs
        self.assertEqual(call_kwargs["messages"], messages)

    def test_chat_includes_system_prompt(self):
        client, mock_sdk = self._make_client()
        client.chat([{"role": "user", "content": "Hi"}], system_prompt="Be concise.")
        call_kwargs = mock_sdk.messages.create.call_args.kwargs
        self.assertEqual(call_kwargs["system"], "Be concise.")

    def test_chat_no_system_prompt_when_empty(self):
        client, mock_sdk = self._make_client()
        client.chat([{"role": "user", "content": "Hi"}], system_prompt="")
        call_kwargs = mock_sdk.messages.create.call_args.kwargs
        self.assertNotIn("system", call_kwargs)

    def test_simple_prompt_wraps_chat(self):
        client, mock_sdk = self._make_client()
        result = client.simple_prompt("Quick question")
        self.assertEqual(result, "This is a mocked response.")
        mock_sdk.messages.create.assert_called_once()

    def test_authentication_error_raises_runtime_error(self):
        import anthropic
        client, mock_sdk = self._make_client()
        mock_sdk.messages.create.side_effect = anthropic.AuthenticationError(
            message="Invalid key", response=MagicMock(), body={}
        )
        with self.assertRaises(RuntimeError):
            client.chat([{"role": "user", "content": "Hi"}])

    def test_rate_limit_error_raises_runtime_error(self):
        import anthropic
        client, mock_sdk = self._make_client()
        mock_sdk.messages.create.side_effect = anthropic.RateLimitError(
            message="Rate limit", response=MagicMock(), body={}
        )
        with self.assertRaises(RuntimeError):
            client.chat([{"role": "user", "content": "Hi"}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
