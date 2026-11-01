"""UI smoke and integration tests for APEX."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from apex.core.database import Database
from apex.ui.main_window import MainWindow
from apex.ui.styles.qss import get_application_stylesheet


@pytest.fixture(scope="session")
def qapp():
    """Ensure QApplication exists for UI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        app.setStyleSheet(get_application_stylesheet())
    return app


def test_main_window_initialization(qapp):
    """Verify MainWindow initializes with all pages and proper dimensions."""
    window = MainWindow()
    assert window.windowTitle().startswith("APEX")
    assert window.stack.count() == 8
    assert window.stack.currentIndex() == 0  # Starts on Home page


def test_navigation_rail_switching(qapp):
    """Verify navigation rail triggers page transitions."""
    window = MainWindow()

    # Navigate to Chat (Index 1)
    window.nav_rail._button_group.button(1).click()
    assert window.stack.currentIndex() == 1

    # Navigate to Settings (Index 7)
    window.nav_rail._button_group.button(7).click()
    assert window.stack.currentIndex() == 7

    # Navigate back to Home (Index 0)
    window.nav_rail._button_group.button(0).click()
    assert window.stack.currentIndex() == 0


def test_home_page_quick_action(qapp):
    """Verify clicking 'Ask APEX' card on Home transitions to Chat page."""
    window = MainWindow()
    assert window.stack.currentIndex() == 0

    # Emit navigate_to directly from Home page
    window.home_page.navigate_to.emit(1)
    assert window.stack.currentIndex() == 1


def test_chat_page_send_message(qapp):
    """Verify sending a message via ChatPage works and persists."""
    window = MainWindow()
    chat_page = window.chat_page

    assert chat_page.active_conv_id is not None
    initial_count = chat_page.messages_layout.count()

    chat_page.message_input.setText("Testing smoke message")
    chat_page.send_message()

    # Layout should now have the user bubble added
    assert chat_page.messages_layout.count() > initial_count
    assert chat_page.message_input.text() == ""

    # Safely wait for background worker to complete
    if chat_page.ai_worker:
        chat_page.ai_worker.wait(1000)


def test_settings_page_persistence(qapp):
    """Verify saving settings updates both the UI state and SQLite."""
    window = MainWindow()
    settings_page = window.settings_page

    settings_page.name_input.setText("APEX Sentinel")
    settings_page.save_settings()

    assert settings_page.feedback_label.text().startswith("✓")

    # Reload from DB
    reloaded_page = window.settings_page
    reloaded_page.load_settings()
    assert reloaded_page.name_input.text() == "APEX Sentinel"


def test_settings_provider_switch_updates_chat_pill(qapp):
    """Verify switching provider in Settings updates ChatPage pill."""
    window = MainWindow()
    settings_page = window.settings_page
    chat_page = window.chat_page

    # Switch to Google Gemini
    idx = settings_page.provider_combo.findData("google_gemini")
    assert idx >= 0
    settings_page.provider_combo.setCurrentIndex(idx)
    settings_page.save_settings()

    assert "Gemini" in chat_page.provider_pill.text()

    # Switch back to Mock
    mock_idx = settings_page.provider_combo.findData("mock")
    settings_page.provider_combo.setCurrentIndex(mock_idx)
    settings_page.save_settings()

    assert "Mock" in chat_page.provider_pill.text()


def test_chat_page_cancel_generation(qapp):
    """Verify canceling generation resets the composer state."""
    window = MainWindow()
    chat_page = window.chat_page

    chat_page.message_input.setText("Compute heavy reasoning task")
    chat_page.send_message()

    # Cancel immediately
    chat_page.cancel_generation()

    assert chat_page.stop_btn.isVisible() is False
    assert chat_page.send_btn.isEnabled() is True
    assert chat_page.thinking_label.isVisible() is False


def test_memory_page_navigation_and_cards(qapp):
    """Verify navigation to MemoryPage and memory card rendering."""
    from apex.core.memory import MemoryService
    window = MainWindow()

    # Navigate to Memory (Index 5)
    window.nav_rail._button_group.button(5).click()
    assert window.stack.currentIndex() == 5

    memory_page = window.memory_page
    MemoryService.add_memory("User prefers dark navy interface", category="preference")
    memory_page.refresh_memories()

    # Check card layout has cards
    assert memory_page.cards_layout.count() >= 2
    assert "Active" in memory_page.pause_btn.text()

    # Toggle pause
    memory_page.pause_btn.click()
    assert "Paused" in memory_page.pause_btn.text()

    # Toggle back to active
    memory_page.pause_btn.click()
    assert "Active" in memory_page.pause_btn.text()


def test_chat_audio_and_push_to_talk(qapp):
    """Verify audio toggle and push-to-talk mic button in ChatPage."""
    window = MainWindow()
    chat_page = window.chat_page

    # Audio output toggle
    initial_text = chat_page.audio_toggle_btn.text()
    chat_page.audio_toggle_btn.click()
    assert chat_page.audio_toggle_btn.text() != initial_text
    chat_page.audio_toggle_btn.click()
    assert chat_page.audio_toggle_btn.text() == initial_text

    # Push to talk button
    chat_page._on_mic_pressed()
    assert chat_page.thinking_label.isHidden() is False
    chat_page._on_mic_released()
    assert chat_page.thinking_label.isHidden() is True
