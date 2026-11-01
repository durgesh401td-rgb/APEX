"""Abstract base class and data structures for AI providers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ProviderResponse(BaseModel):
    """Normalized response returned by any AI provider adapter."""

    content: str
    model_name: str
    success: bool = True
    error_message: Optional[str] = None
    finish_reason: Optional[str] = "stop"
    usage_info: Dict[str, int] = Field(default_factory=dict)


class BaseAIProvider(ABC):
    """Abstract interface for AI model providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier (e.g. 'mock', 'google_gemini')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable display name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short summary of the provider capabilities."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if required credentials or endpoints are available."""
        pass

    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """Test API connectivity and key validity."""
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> ProviderResponse:
        """Generate a response given a list of messages [{'role': ..., 'content': ...}]."""
        pass
