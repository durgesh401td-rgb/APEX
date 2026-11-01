"""Google Gemini API provider adapter using official google-genai SDK."""

import os
from typing import Dict, List, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError
from apex.core.credentials import credentials
from apex.core.logging import logger
from apex.core.providers.base import BaseAIProvider, ProviderResponse

CREDENTIAL_KEY = "GEMINI_API_KEY"
DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiAIProvider(BaseAIProvider):
    """Adapter for Google Gemini API models (free tier compatible)."""

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name

    @property
    def provider_id(self) -> str:
        return "google_gemini"

    @property
    def display_name(self) -> str:
        return f"Google Gemini ({self.model_name})"

    @property
    def description(self) -> str:
        return (
            "Fast, highly capable cloud reasoning via Google Gemini API. "
            "Free tier eligible (15 requests/min at ₹0 cost)."
        )

    def _get_api_key(self) -> Optional[str]:
        """Fetch API key from OS Credential Manager or environment variable."""
        key = credentials.get_credential(CREDENTIAL_KEY)
        if not key:
            key = os.environ.get("GEMINI_API_KEY")
        return key

    def is_configured(self) -> bool:
        """Check if an API key is available."""
        key = self._get_api_key()
        return bool(key and len(key.strip()) > 5)

    def _get_client(self) -> Optional[genai.Client]:
        """Instantiate Google GenAI Client."""
        api_key = self._get_api_key()
        if not api_key:
            return None
        return genai.Client(api_key=api_key)

    def test_connection(self) -> tuple[bool, str]:
        """Verify API key connectivity with Google Gemini."""
        if not self.is_configured():
            return False, "No Gemini API key found in OS Credential Manager."

        client = self._get_client()
        if not client:
            return False, "Failed to initialize Gemini client."

        try:
            # Simple test call
            response = client.models.generate_content(
                model=self.model_name,
                contents="Hello, reply with only the word 'OK'.",
                config=types.GenerateContentConfig(max_output_tokens=10),
            )
            if response and response.text:
                return True, f"Successfully connected to Google Gemini ({self.model_name})!"
            return False, "Received empty response from Gemini API."
        except APIError as e:
            logger.warning("Gemini API connection test failed: %s", e.message)
            return False, f"Gemini API Error ({e.code}): {e.message}"
        except Exception as e:
            logger.warning("Network or client error during connection test: %s", str(e))
            return False, f"Connection error: {str(e)}"

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> ProviderResponse:
        """Generate a response using Google Gemini."""
        if not self.is_configured():
            return ProviderResponse(
                content=(
                    "⚠️ Google Gemini API key is missing.\n\n"
                    "Please navigate to Settings → AI Provider and enter your free Gemini API key. "
                    "Keys are securely stored in Windows Credential Manager."
                ),
                model_name=self.model_name,
                success=False,
                error_message="Missing API key",
            )

        client = self._get_client()
        if not client:
            return ProviderResponse(
                content="Failed to initialize Gemini client.",
                model_name=self.model_name,
                success=False,
                error_message="Client initialization error",
            )

        # Build contents from message history
        # Map roles: 'user' -> 'user', 'assistant' -> 'model'
        contents = []
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "model"
            content = msg.get("content", "").strip()
            if content:
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=content)],
                    )
                )

        if not contents:
            return ProviderResponse(
                content="No message content provided.",
                model_name=self.model_name,
                success=False,
                error_message="Empty input",
            )

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            system_instruction=system_prompt or "You are APEX, a helpful, precise personal AI assistant for Windows.",
        )

        try:
            logger.info("Calling Gemini API (%s) with %d messages", self.model_name, len(contents))
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            response_text = response.text or ""
            return ProviderResponse(
                content=response_text,
                model_name=self.model_name,
                success=True,
                finish_reason="stop",
            )
        except APIError as e:
            logger.error("Gemini API call failed with code %s: %s", e.code, e.message)
            return ProviderResponse(
                content=f"⚠️ Gemini API Error ({e.code}): {e.message}",
                model_name=self.model_name,
                success=False,
                error_message=e.message,
            )
        except Exception as e:
            logger.error("Unexpected error during Gemini generation: %s", str(e))
            return ProviderResponse(
                content=f"⚠️ Network error while connecting to Gemini: {str(e)}",
                model_name=self.model_name,
                success=False,
                error_message=str(e),
            )
