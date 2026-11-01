"""Tests for AI provider adapters and secure credential storage."""

import pytest
from apex.core.credentials import CredentialManager
from apex.core.providers.gemini_provider import GeminiAIProvider
from apex.core.providers.mock_provider import MockAIProvider
from apex.core.providers.registry import ProviderRegistry


def test_credential_manager_roundtrip():
    """Verify storing, retrieving, checking, and deleting credentials."""
    test_key = "APEX_TEST_SECRET_KEY"
    test_secret = "test-secret-value-12345"

    # Store
    saved = CredentialManager.save_credential(test_key, test_secret)
    assert saved is True

    # Retrieve
    retrieved = CredentialManager.get_credential(test_key)
    assert retrieved == test_secret
    assert CredentialManager.has_credential(test_key) is True

    # Delete
    deleted = CredentialManager.delete_credential(test_key)
    assert deleted is True
    assert CredentialManager.get_credential(test_key) is None
    assert CredentialManager.has_credential(test_key) is False


def test_mock_provider_generation():
    """Verify MockAIProvider generates formatted responses."""
    provider = MockAIProvider()
    assert provider.provider_id == "mock"
    assert provider.is_configured() is True

    ok, msg = provider.test_connection()
    assert ok is True

    messages = [
        {"role": "user", "content": "What is the status of APEX?"}
    ]
    resp = provider.generate(messages)
    assert resp.success is True
    assert "status" in resp.content.lower() or "health" in resp.content.lower()


def test_gemini_provider_unconfigured():
    """Verify GeminiAIProvider gracefully handles unconfigured state."""
    provider = GeminiAIProvider()
    if not provider.is_configured():
        ok, msg = provider.test_connection()
        assert ok is False
        assert "gemini api key" in msg.lower() or "missing" in msg.lower()

        resp = provider.generate([{"role": "user", "content": "Hello"}])
        assert resp.success is False
        assert "missing" in resp.content.lower() or "api key" in resp.content.lower()


def test_provider_registry():
    """Verify ProviderRegistry lists providers and switches active provider."""
    reg = ProviderRegistry()
    providers = reg.list_providers()
    assert len(providers) >= 2

    ids = [p.provider_id for p in providers]
    assert "mock" in ids
    assert "google_gemini" in ids

    # Test switching
    assert reg.set_active_provider("mock") is True
    active = reg.get_active_provider()
    assert active.provider_id == "mock"

    # Test invalid provider
    assert reg.set_active_provider("unknown_provider_xyz") is False
