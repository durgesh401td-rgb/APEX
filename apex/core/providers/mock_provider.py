"""Offline mock provider for testing and offline desktop operation."""

import time
from typing import Dict, List, Optional
from apex.core.providers.base import BaseAIProvider, ProviderResponse


class MockAIProvider(BaseAIProvider):
    """Local offline provider that simulates AI reasoning without external network calls."""

    @property
    def provider_id(self) -> str:
        return "mock"

    @property
    def display_name(self) -> str:
        return "Offline Mock Assistant"

    @property
    def description(self) -> str:
        return "Offline fallback mode running locally with zero network calls and ₹0 cost."

    def is_configured(self) -> bool:
        return True

    def test_connection(self) -> tuple[bool, str]:
        return True, "Offline engine is operational and ready."

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> ProviderResponse:
        # Simulate slight processing latency (200ms)
        time.sleep(0.2)

        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").strip()
                break

        query = last_user_msg.lower()

        if "hello" in query or "hi" in query or "hey" in query:
            text = (
                "Hello! I am APEX, running in offline mode. I can persist our conversations "
                "locally, configure your settings, and execute local tasks."
            )
        elif "status" in query or "health" in query:
            text = (
                "APEX System Health: All local subsystems nominal.\n"
                "- Memory & CPU: Optimized for dual-core Intel Core i3 / 8 GB RAM\n"
                "- Persistence: SQLite database active\n"
                "- AI Engine: Pluggable Adapter Interface (Stage 2)"
            )
        elif "roadmap" in query:
            text = (
                "APEX Roadmap Status:\n"
                "- Stage 1 (Core Desktop): Complete\n"
                "- Stage 2 (AI Provider Connection): Active\n"
                "- Stage 3 (Memory Vault): Upcoming\n"
                "- Stage 4 (Voice & Wake Word): Upcoming\n"
                "- Stage 5 (Safe PC Automation): Upcoming"
            )
        elif "help" in query:
            text = (
                "You can ask me questions, test conversation persistence, or switch "
                "to the Google Gemini API provider in Settings to enable live cloud reasoning."
            )
        else:
            text = (
                f"Received your message: \"{last_user_msg}\".\n\n"
                "I am currently operating using the local offline provider. "
                "To unlock live cloud reasoning, add your free Google Gemini API key in Settings → AI Provider."
            )

        return ProviderResponse(
            content=text,
            model_name="apex-mock-v1",
            success=True,
            finish_reason="stop",
            usage_info={"prompt_tokens": len(last_user_msg.split()), "completion_tokens": len(text.split())},
        )
