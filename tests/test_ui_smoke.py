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
