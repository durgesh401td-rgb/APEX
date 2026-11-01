"""Tests for APEX core configuration and logging security."""

from apex.core.config import AppConfig
from apex.core.logging import SensitiveDataFilter


def test_default_config():
    """Verify default design tokens and application configuration."""
    cfg = AppConfig()
    assert cfg.app_name == "APEX"
    assert cfg.wake_phrase == "Hey Apex!!!"
    assert cfg.bg_primary == "#080B12"
    assert cfg.surface_primary == "#111827"
    assert cfg.accent_primary == "#168BFF"
    assert cfg.accent_secondary == "#00D9FF"
    assert cfg.window_width == 1280
    assert cfg.window_height == 720


def test_sensitive_data_filter_redacts():
    """Verify sensitive tokens and keys are sanitized from log entries."""
    filter_ = SensitiveDataFilter()
    sample_text = "Connecting with api_key: 'AIzaSyDx49kLmNoPqrStUvWxYz0123456789abc' and sk-abcdef1234567890abcdef"
    sanitized = filter_.sanitize(sample_text)
    assert "AIzaSy" not in sanitized
    assert "sk-abcdef" not in sanitized
    assert "[REDACTED]" in sanitized
