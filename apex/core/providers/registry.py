"""Registry for discovering, selecting, and managing AI providers."""

from typing import Dict, List, Optional
from apex.core.database import db
from apex.core.logging import logger
from apex.core.providers.base import BaseAIProvider
from apex.core.providers.gemini_provider import GeminiAIProvider
from apex.core.providers.mock_provider import MockAIProvider

SETTING_ACTIVE_PROVIDER = "active_ai_provider"


class ProviderRegistry:
    """Manages available AI providers and the current active engine."""

    def __init__(self):
        self._providers: Dict[str, BaseAIProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self) -> None:
        self.register(MockAIProvider())
        self.register(GeminiAIProvider(model_name="gemini-2.5-flash"))

    def register(self, provider: BaseAIProvider) -> None:
        """Register a new provider adapter."""
        self._providers[provider.provider_id] = provider
        logger.debug("Registered AI provider: %s (%s)", provider.provider_id, provider.display_name)

    def list_providers(self) -> List[BaseAIProvider]:
        """Return a list of all registered providers."""
        return list(self._providers.values())

    def get_provider(self, provider_id: str) -> Optional[BaseAIProvider]:
        """Get a specific provider by its ID."""
        return self._providers.get(provider_id)

    def get_active_provider_id(self) -> str:
        """Get the ID of the currently active provider from SQLite settings."""
        # Default to 'mock' if not set
        return db.get_setting(SETTING_ACTIVE_PROVIDER, default="mock")

    def set_active_provider(self, provider_id: str) -> bool:
        """Set the active provider ID in SQLite settings."""
        if provider_id not in self._providers:
            logger.warning("Attempted to set unknown provider: %s", provider_id)
            return False
        db.set_setting(SETTING_ACTIVE_PROVIDER, provider_id)
        logger.info("Active AI provider switched to: %s", provider_id)
        return True

    def get_active_provider(self) -> BaseAIProvider:
        """Return the active provider instance with automatic fallback to mock."""
        active_id = self.get_active_provider_id()
        provider = self.get_provider(active_id)
        if provider:
            return provider

        # Fallback to mock
        logger.warning("Active provider '%s' not found. Falling back to mock.", active_id)
        return self._providers["mock"]


# Global registry singleton
registry = ProviderRegistry()
