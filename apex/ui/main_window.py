"""Main application window shell for APEX."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)
from apex.core.config import config
from apex.ui.pages.chat_page import ChatPage
from apex.ui.pages.home_page import HomePage
from apex.ui.pages.placeholder_page import PlaceholderPage
from apex.ui.pages.settings_page import SettingsPage
from apex.ui.widgets.nav_rail import NavRail


class MainWindow(QMainWindow):
    """APEX primary desktop application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{config.app_name} — {config.tagline}")
        self.resize(config.window_width, config.window_height)
        self.setMinimumSize(config.min_width, config.min_height)
        self._init_ui()

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Persistent Left Navigation Rail
        self.nav_rail = NavRail(self)
        root_layout.addWidget(self.nav_rail)

        # Central Stacked Viewport
        self.stack = QStackedWidget(self)

        # Pages corresponding to nav rail indexes (0 - 7)
        self.home_page = HomePage(self)
        self.chat_page = ChatPage(self)
        self.tools_page = PlaceholderPage(
            "Tool Registry",
            "Searchable catalogue of typed, permission-gated system tools and actions.",
            "Stage 5 (Safe PC Automation)",
            "🛠️",
            self
        )
        self.automation_page = PlaceholderPage(
            "Automation Guard",
            "Workflows, background tasks, audit trail, and emergency stop controls.",
            "Stage 5 (Safe PC Automation)",
            "⚙️",
            self
        )
        self.files_page = PlaceholderPage(
            "Document & File Vault",
            "Approved file tasks, screenshots, and document workspace.",
            "Stage 7 (Vision & Research)",
            "📁",
            self
        )
        self.memory_page = PlaceholderPage(
            "User Memory Vault",
            "Inspect, edit, pause, and clear long-term memory facts with complete control.",
            "Stage 3 (Memory)",
            "🧠",
            self
        )
        self.devices_page = PlaceholderPage(
            "Device Companion",
            "Authenticated, encrypted local Wi-Fi pairing for Android notifications and media sync.",
            "Stage 6 (Android Companion)",
            "📱",
            self
        )
        self.settings_page = SettingsPage(self)

        self.stack.addWidget(self.home_page)       # 0
        self.stack.addWidget(self.chat_page)       # 1
        self.stack.addWidget(self.tools_page)      # 2
        self.stack.addWidget(self.automation_page) # 3
        self.stack.addWidget(self.files_page)      # 4
        self.stack.addWidget(self.memory_page)     # 5
        self.stack.addWidget(self.devices_page)    # 6
        self.stack.addWidget(self.settings_page)   # 7

        root_layout.addWidget(self.stack)

        # Connect Navigation Signals
        self.nav_rail.page_changed.connect(self._on_navigation)
        self.home_page.navigate_to.connect(self._on_home_navigation)

    def _on_navigation(self, page_index: int) -> None:
        self.stack.setCurrentIndex(page_index)

    def _on_home_navigation(self, page_index: int) -> None:
        self.nav_rail.set_active_page(page_index)
        self.stack.setCurrentIndex(page_index)
