"""Settings page for APEX."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from apex.core.config import config
from apex.core.database import db
from apex.core.logging import logger
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


class SettingsPage(QWidget):
    """Settings management page for appearance, AI provider, and system preferences."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.load_settings()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------------------------------------------------------------
        # Left Sub-Navigation for Settings Categories
        # ---------------------------------------------------------------------
        sub_nav = QFrame()
        sub_nav.setFixedWidth(200)
        sub_nav.setStyleSheet(
            f"background-color: {SURFACE_PRIMARY}; border-right: 1px solid {BORDER_COLOR};"
        )
        sub_layout = QVBoxLayout(sub_nav)
        sub_layout.setContentsMargins(14, 20, 14, 20)
        sub_layout.setSpacing(6)

        title = QLabel("Settings")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY}; margin-bottom: 12px;")
        sub_layout.addWidget(title)

        categories = [
            ("General", 0),
            ("AI Provider", 1),
            ("Appearance", 2),
            ("Security & Privacy", 3),
            ("About", 4),
        ]

        self._nav_buttons = []
        for name, idx in categories:
            btn = QPushButton(name)
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, i=idx: self._switch_tab(i))
            self._nav_buttons.append(btn)
            sub_layout.addWidget(btn)

        sub_layout.addStretch()
        main_layout.addWidget(sub_nav)

        # ---------------------------------------------------------------------
        # Right Stacked Settings Panels
        # ---------------------------------------------------------------------
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(40, 30, 40, 30)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._create_general_tab())
        self.stack.addWidget(self._create_ai_provider_tab())
        self.stack.addWidget(self._create_appearance_tab())
        self.stack.addWidget(self._create_security_tab())
        self.stack.addWidget(self._create_about_tab())

        content_layout.addWidget(self.stack)

        # Bottom Save and Feedback Bar
        save_bar = QHBoxLayout()
        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet(f"color: {STATUS_ONLINE}; font-weight: 600; font-size: 13px;")

        save_btn = QPushButton("Save Preferences")
        save_btn.setProperty("class", "action-btn")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_settings)

        save_bar.addWidget(self.feedback_label)
        save_bar.addStretch()
        save_bar.addWidget(save_btn)
        content_layout.addLayout(save_bar)

        main_layout.addWidget(content_container)

    def _switch_tab(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)

    # -------------------------------------------------------------------------
    # Panels
    # -------------------------------------------------------------------------

    def _create_general_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(18)

        heading = QLabel("General Settings")
        heading.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY};")
        desc = QLabel("Configure product identity, name, and default wake word.")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")

        layout.addWidget(heading)
        layout.addWidget(desc)

        card = QFrame()
        card.setProperty("class", "content-card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        card_layout.addWidget(QLabel("Assistant Display Name:"))
        self.name_input = QLineEdit()
        card_layout.addWidget(self.name_input)

        card_layout.addWidget(QLabel("Wake Phrase (Stage 4 Local Engine):"))
        self.wake_input = QLineEdit()
        card_layout.addWidget(self.wake_input)

        layout.addWidget(card)
        layout.addStretch()
        return w

    def _create_ai_provider_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(18)

        heading = QLabel("AI Provider Configuration")
        heading.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY};")
        desc = QLabel("APEX connects to external AI models through safe, replaceable adapters.")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")

        layout.addWidget(heading)
        layout.addWidget(desc)

        card = QFrame()
        card.setProperty("class", "content-card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        card_layout.addWidget(QLabel("Active AI Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.setStyleSheet(
            f"background-color: {SURFACE_ELEVATED}; color: {TEXT_PRIMARY}; padding: 8px 12px; border: 1px solid {BORDER_COLOR}; border-radius: 8px;"
        )
        self.provider_combo.addItems([
            "Offline Mock Assistant (Stage 1 Default)",
            "Google Gemini API (Stage 2 Free Tier Candidate)",
            "Local Ollama / Llama.cpp (Optional)",
            "Custom Provider Adapter"
        ])
        card_layout.addWidget(self.provider_combo)

        notice_box = QFrame()
        notice_box.setStyleSheet("background-color: #0E1522; border-radius: 8px; padding: 12px;")
        notice_layout = QVBoxLayout(notice_box)
        notice_title = QLabel("🔒 Zero Secret Storage Rule")
        notice_title.setStyleSheet(f"color: {ACCENT_CYAN}; font-weight: 700; font-size: 12px;")
        notice_body = QLabel(
            "API keys and credentials are never stored in source files, plain text, or SQLite. "
            "Stage 2 will wire secure storage directly to Windows Credential Manager."
        )
        notice_body.setWordWrap(True)
        notice_body.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        notice_layout.addWidget(notice_title)
        notice_layout.addWidget(notice_body)
        card_layout.addWidget(notice_box)

        layout.addWidget(card)
        layout.addStretch()
        return w

    def _create_appearance_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(18)

        heading = QLabel("Appearance & Theme")
        heading.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY};")
        desc = QLabel("Customize theme tokens, colors, and motion settings.")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")

        layout.addWidget(heading)
        layout.addWidget(desc)

        card = QFrame()
        card.setProperty("class", "content-card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        card_layout.addWidget(QLabel("Application Theme:"))
        theme_lbl = QLabel("Dark, Clean & Spacious (Near-black navy #080B12)")
        theme_lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-weight: 600;")
        card_layout.addWidget(theme_lbl)

        card_layout.addWidget(QLabel("Primary Accent Color:"))
        self.accent_combo = QComboBox()
        self.accent_combo.setStyleSheet(
            f"background-color: {SURFACE_ELEVATED}; color: {TEXT_PRIMARY}; padding: 8px 12px; border: 1px solid {BORDER_COLOR}; border-radius: 8px;"
        )
        self.accent_combo.addItems([
            "Electric Blue (#168BFF) - Default",
            "Cyan Glow (#00D9FF)",
            "Emerald (#10B981)"
        ])
        card_layout.addWidget(self.accent_combo)

        layout.addWidget(card)
        layout.addStretch()
        return w

    def _create_security_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(18)

        heading = QLabel("Security & Privacy Guardrails")
        heading.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY};")

        card = QFrame()
        card.setProperty("class", "content-card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        items = [
            ("No Autonomous Execution", "APEX cannot run arbitrary shell commands without your policy confirmation."),
            ("Local-First Storage", "All chat history and preferences are saved locally on your machine in SQLite."),
            ("Zero Cloud Telemetry", "No background data or analytics are uploaded to any external server."),
            ("Emergency Stop Support", "UI and shortcut controls will halt running background tasks immediately.")
        ]

        for title, detail in items:
            t = QLabel(f"✔  {title}")
            t.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-weight: 700; font-size: 13px;")
            d = QLabel(detail)
            d.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; margin-left: 20px; margin-bottom: 6px;")
            card_layout.addWidget(t)
            card_layout.addWidget(d)

        layout.addWidget(heading)
        layout.addWidget(card)
        layout.addStretch()
        return w

    def _create_about_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(14)

        heading = QLabel("About APEX")
        heading.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY};")

        card = QFrame()
        card.setProperty("class", "content-card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        card_layout.addWidget(QLabel("<b>Project:</b> APEX (Think • Assist • Achieve)"))
        card_layout.addWidget(QLabel("<b>Version:</b> 0.1.0 (Stage 1 Core Desktop Baseline)"))
        card_layout.addWidget(QLabel("<b>Host:</b> Dell Inspiron 15-3567 / Intel Core i3-7020U / 8 GB RAM"))
        card_layout.addWidget(QLabel("<b>Operating System:</b> Windows 10 Home (Build 19045.7807, 22H2)"))
        card_layout.addWidget(QLabel("<b>License & Budget:</b> Open Source / Personal Project / ₹0 Initial Budget"))

        layout.addWidget(heading)
        layout.addWidget(card)
        layout.addStretch()
        return w

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------

    def load_settings(self) -> None:
        """Load settings from SQLite database or fallback to defaults."""
        app_name = db.get_setting("app_name", config.app_name)
        wake_phrase = db.get_setting("wake_phrase", config.wake_phrase)
        provider = db.get_setting("ai_provider", "0")

        self.name_input.setText(app_name)
        self.wake_input.setText(wake_phrase)
        try:
            self.provider_combo.setCurrentIndex(int(provider))
        except (ValueError, TypeError):
            self.provider_combo.setCurrentIndex(0)

    def save_settings(self) -> None:
        """Persist modified settings to SQLite."""
        db.set_setting("app_name", self.name_input.text().strip() or config.app_name)
        db.set_setting("wake_phrase", self.wake_input.text().strip() or config.wake_phrase)
        db.set_setting("ai_provider", str(self.provider_combo.currentIndex()))

        logger.info("Application settings saved to SQLite")
        self.feedback_label.setText("✓ Settings saved successfully")
