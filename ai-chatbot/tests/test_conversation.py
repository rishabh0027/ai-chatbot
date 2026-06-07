"""
tests/test_conversation.py
--------------------------
Unit tests for ConversationMemory and Conversation orchestrator.

Uses unittest.mock to patch the LLM client so tests run without
a real API key or internet connection.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory import ConversationMemory, Message
from features.persona import PersonaManager


class TestConversationMemory(unittest.TestCase):
    """Tests for the ConversationMemory class."""

    def setUp(self):
        self.memory = ConversationMemory(max_messages=5)

    def test_add_message(self):
        self.memory.add("user", "Hello!")
        self.assertEqual(self.memory.message_count, 1)

    def test_roles_preserved(self):
        self.memory.add("user", "Hi")
        self.memory.add("assistant", "Hello!")
        messages = self.memory.get_all()
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[1].role, "assistant")

    def test_sliding_window_enforced(self):
        for i in range(10):
            self.memory.add("user", f"Message {i}")
        # Should never exceed max_messages
        self.assertLessEqual(self.memory.message_count, 5)

    def test_clear_wipes_history(self):
        self.memory.add("user", "Test")
        self.memory.clear()
        self.assertEqual(self.memory.message_count, 0)

    def test_get_api_messages_format(self):
        self.memory.add("user", "Hi")
        self.memory.add("assistant", "Hello")
        api_msgs = self.memory.get_api_messages()
        self.assertIsInstance(api_msgs, list)
        self.assertTrue(all("role" in m and "content" in m for m in api_msgs))

    def test_summary_injected_in_api_messages(self):
        self.memory.set_summary("Earlier we discussed Python.")
        self.memory.add("user", "What else?")
        api_msgs = self.memory.get_api_messages()
        # Summary pair + the real message = 3 messages minimum
        self.assertGreaterEqual(len(api_msgs), 3)
        contents = [m["content"] for m in api_msgs]
        self.assertTrue(any("Earlier we discussed Python" in c for c in contents))

    def test_needs_summarization_flag(self):
        memory = ConversationMemory(max_messages=20)
        # Below threshold
        for i in range(5):
            memory.add("user", f"msg {i}")
        self.assertFalse(memory.needs_summarization)

    def test_sentiment_stored_on_message(self):
        self.memory.add("user", "I am so happy!", sentiment="positive")
        msg: Message = self.memory.get_all()[0]
        self.assertEqual(msg.sentiment, "positive")


class TestPersonaManager(unittest.TestCase):
    """Tests for the PersonaManager class."""

    def setUp(self):
        self.pm = PersonaManager(default="assistant")

    def test_default_persona(self):
        self.assertEqual(self.pm.current_name, "Assistant")

    def test_switch_valid_persona(self):
        result = self.pm.switch("teacher")
        self.assertTrue(result)
        self.assertEqual(self.pm.current_name, "Teacher")

    def test_switch_invalid_persona(self):
        result = self.pm.switch("nonexistent_persona")
        self.assertFalse(result)
        # Persona should remain unchanged
        self.assertEqual(self.pm.current_name, "Assistant")

    def test_switch_case_insensitive(self):
        result = self.pm.switch("TEACHER")
        self.assertTrue(result)

    def test_system_prompt_non_empty(self):
        prompt = self.pm.get_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 10)

    def test_list_personas(self):
        personas = self.pm.list_personas()
        self.assertIn("assistant", personas)
        self.assertIn("teacher", personas)
        self.assertIn("debugger", personas)

    def test_system_prompt_changes_with_persona(self):
        prompt_before = self.pm.get_system_prompt()
        self.pm.switch("debugger")
        prompt_after = self.pm.get_system_prompt()
        self.assertNotEqual(prompt_before, prompt_after)


class TestConversationIntegration(unittest.TestCase):
    """
    Integration tests for the Conversation class.
    LLMClient is fully mocked — no API calls are made.
    """

    def _make_conversation(self, reply="Mocked reply"):
        """Helper: create a Conversation with a mocked LLMClient."""
        with patch("core.conversation.LLMClient") as MockClient:
            instance = MockClient.return_value
            instance.chat.return_value = reply
            instance.simple_prompt.return_value = "neutral"

            from core.conversation import Conversation
            conv = Conversation()
            conv.client = instance          # inject mock
            conv.sentiment_analyser._client = instance
            conv.summarizer._client = instance
            return conv

    def test_send_returns_string(self):
        conv = self._make_conversation("Hello! How can I help?")
        reply = conv.send("Hi there")
        self.assertIsInstance(reply, str)

    def test_memory_grows_after_send(self):
        conv = self._make_conversation()
        conv.send("First message")
        # User + assistant = 2 messages
        self.assertEqual(conv.memory.message_count, 2)

    def test_persona_switch(self):
        conv = self._make_conversation()
        result = conv.switch_persona("teacher")
        self.assertTrue(result)
        self.assertEqual(conv.current_persona, "Teacher")

    def test_clear_resets_memory(self):
        conv = self._make_conversation()
        conv.send("Some message")
        conv.clear()
        self.assertEqual(conv.memory.message_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
