"""Home dashboard page for APEX."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from apex.core.config import config
from apex.ui.styles.palette import (
    ACCENT_CYAN,
    ACCENT_PRIMARY,
    BORDER_COLOR,
    STATUS_ONLINE,
    SURFACE_ELEVATED,
    SURFACE_PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from apex.ui.widgets.visualizer import ApexVisualizer


class ActionCard(QFrame):
    """Interactive quick action card with icon, title, and description."""

    clicked = Signal()

    def __init__(self, title: str, desc: str, icon: str, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            ActionCard {{
                background-color: {SURFACE_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
                padding: 16px;
            }}
            ActionCard:hover {{
                background-color: {SURFACE_ELEVATED};
                border: 1px solid {ACCENT_PRIMARY};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        # Header with icon & title
        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 20px; color: {ACCENT_CYAN};")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY};")
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()

        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY}; line-height: 1.3;")

        layout.addLayout(header)
        layout.addWidget(desc_lbl)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class HomePage(QWidget):
    """Central Home dashboard page."""

    navigate_to = Signal(int)  # Emit page index to switch to

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 36, 40, 30)
        main_layout.setSpacing(24)

        # Top Greeting and Energy Core Section
        hero_section = QVBoxLayout()
        hero_section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_section.setSpacing(12)

        # Visualizer Core
        self.visualizer = ApexVisualizer(self, size=150)
        hero_section.addWidget(self.visualizer, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title & Subtitle
        title_label = QLabel(f"Welcome to {config.app_name}")
        title_label.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {TEXT_PRIMARY}; letter-spacing: 1px;"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Think • Assist • Achieve  —  Your Personal AI Companion")
        subtitle_label.setStyleSheet(
            f"font-size: 14px; font-weight: 500; color: {TEXT_SECONDARY};"
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        prompt_label = QLabel("How can I assist your workflow today?")
        prompt_label.setStyleSheet(
            f"font-size: 13px; color: {TEXT_MUTED}; margin-top: 4px;"
        )
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hero_section.addWidget(title_label)
        hero_section.addWidget(subtitle_label)
        hero_section.addWidget(prompt_label)
        main_layout.addLayout(hero_section)

        main_layout.addSpacerItem(QSpacerItem(20, 16, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Quick Actions Grid (3-4 cards max as per 03_UI_UX_SPEC.md)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)

        card1 = ActionCard(
            "Ask APEX",
            "Open conversation workspace to query, brainstorm, or compose.",
            "💬"
        )
        card1.clicked.connect(lambda: self.navigate_to.emit(1))  # Switch to Chat

        card2 = ActionCard(
            "Explore Tools",
            "Catalogue of safe, permission-gated system and workflow tools.",
            "🛠️"
        )
        card2.clicked.connect(lambda: self.navigate_to.emit(2))  # Switch to Tools

        card3 = ActionCard(
            "System Settings",
            "Configure appearance, local AI provider, and privacy controls.",
            "🔧"
        )
        card3.clicked.connect(lambda: self.navigate_to.emit(7))  # Switch to Settings

        card4 = ActionCard(
            "Automation Guard",
            "Inspect pre-approved tasks and verify automation permissions.",
            "⚙️"
        )
        card4.clicked.connect(lambda: self.navigate_to.emit(3))  # Switch to Automation

        grid_layout.addWidget(card1, 0, 0)
        grid_layout.addWidget(card2, 0, 1)
        grid_layout.addWidget(card3, 1, 0)
        grid_layout.addWidget(card4, 1, 1)

        main_layout.addLayout(grid_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Bottom System Diagnostics Bar
        system_bar = QFrame()
        system_bar.setStyleSheet(
            f"background-color: {SURFACE_PRIMARY}; border: 1px solid {BORDER_COLOR}; border-radius: 10px; padding: 12px 20px;"
        )
        bar_layout = QHBoxLayout(system_bar)
        bar_layout.setContentsMargins(12, 6, 12, 6)

        diag_icon = QLabel("🛡️")
        diag_title = QLabel("Security Status: Local-first Sandbox Active")
        diag_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 500;")

        env_info = QLabel("Python 3.12 • SQLite Engine • Zero External Cloud Calls")
        env_info.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")

        bar_layout.addWidget(diag_icon)
        bar_layout.addWidget(diag_title)
        bar_layout.addStretch()
        bar_layout.addWidget(env_info)

        main_layout.addWidget(system_bar)
