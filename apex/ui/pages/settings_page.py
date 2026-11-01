"""Settings page for APEX with secure Windows Credential Manager integration."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from apex.core.config import config
from apex.core.credentials import credentials
from apex.core.database import db
from apex.core.logging import logger
from apex.core.providers.gemini_provider import CREDENTIAL_KEY as GEMINI_KEY_NAME
from apex.core.providers.registry import registry
from apex.ui.styles.palette import (
    ACCENT_CYAN,
    ACCENT_PRIMARY,
    BORDER_COLOR,
    STATUS_ERROR,
    STATUS_ONLINE,
    STATUS_WARNING,
    SURFACE_ELEVATED,
    SURFACE_PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class SettingsPage(QWidget):
    """Settings management page for appearance, AI provider, and system preferences."""

    provider_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._nav_buttons = []
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

        # Provider Selector Card
        card = QFrame()
        card.setProperty("class", "content-card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        card_layout.addWidget(QLabel("Active AI Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.setStyleSheet(
            f"background-color: {SURFACE_ELEVATED}; color: {TEXT_PRIMARY}; padding: 8px 12px; border: 1px solid {BORDER_COLOR}; border-radius: 8px;"
        )
        self.provider_combo.addItem("Offline Mock Assistant (Zero Cost / Offline)", "mock")
        self.provider_combo.addItem("Google Gemini API (Free Tier: 15 RPM / ₹0)", "google_gemini")
        self.provider_combo.currentIndexChanged.connect(self._on_provider_selection_changed)
        card_layout.addWidget(self.provider_combo)

        # Gemini API Key Management Sub-card
        self.key_container = QFrame()
        self.key_container.setStyleSheet(
            f"background-color: {SURFACE_ELEVATED}; border: 1px solid {BORDER_COLOR}; border-radius: 10px; padding: 14px;"
        )
        key_layout = QVBoxLayout(self.key_container)
        key_layout.setSpacing(10)

        key_title = QLabel("Google Gemini API Key (Stored in Windows Credential Manager):")
        key_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 12px;")
        key_layout.addWidget(key_title)

        key_input_row = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Enter your Gemini API key (AIzaSy...)")
        key_input_row.addWidget(self.key_input)

        save_key_btn = QPushButton("Save Key")
        save_key_btn.setProperty("class", "action-btn")
        save_key_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_key_btn.clicked.connect(self._save_gemini_key)
        key_input_row.addWidget(save_key_btn)

        remove_key_btn = QPushButton("Remove Key")
        remove_key_btn.setProperty("class", "secondary-btn")
        remove_key_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_key_btn.clicked.connect(self._remove_gemini_key)
        key_input_row.addWidget(remove_key_btn)

        key_layout.addLayout(key_input_row)

        # Status and Test Connection row
        test_row = QHBoxLayout()
        self.key_status_label = QLabel("")
        self.key_status_label.setStyleSheet("font-size: 11px;")

        test_btn = QPushButton("⚡ Test API Connection")
        test_btn.setProperty("class", "secondary-btn")
        test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        test_btn.clicked.connect(self._test_gemini_connection)

        test_row.addWidget(self.key_status_label)
        test_row.addStretch()
        test_row.addWidget(test_btn)
        key_layout.addLayout(test_row)

        self.test_result_label = QLabel("")
        self.test_result_label.setWordWrap(True)
        self.test_result_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        key_layout.addWidget(self.test_result_label)

        card_layout.addWidget(self.key_container)

        # Security Note Card
        notice_box = QFrame()
        notice_box.setStyleSheet("background-color: #0E1522; border-radius: 8px; padding: 12px;")
        notice_layout = QVBoxLayout(notice_box)
        notice_title = QLabel("🔒 Windows Credential Vault Guardrail")
        notice_title.setStyleSheet(f"color: {ACCENT_CYAN}; font-weight: 700; font-size: 12px;")
        notice_body = QLabel(
            "API keys are encrypted and stored in Windows Credential Manager. "
            "They are never written to source files, plain text, SQLite, or log outputs."
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
            ("Windows Credential Manager", "Secrets and API keys are stored in the OS-backed DPAPI encrypted vault."),
            ("No Autonomous Shell Execution", "The AI model cannot execute arbitrary shell commands on your system."),
            ("Local-First SQLite", "Chat history and settings remain locally on your SSD/HDD."),
            ("Strict Redaction Logging", "All logs are automatically filtered so no sensitive keys or tokens are stored.")
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
        card_layout.addWidget(QLabel("<b>Version:</b> 0.2.0 (Stage 2 AI Connection)"))
        card_layout.addWidget(QLabel("<b>Host:</b> Dell Inspiron 15-3567 / Intel Core i3-7020U / 8 GB RAM"))
        card_layout.addWidget(QLabel("<b>Operating System:</b> Windows 10 Home (Build 19045.7807, 22H2)"))
        card_layout.addWidget(QLabel("<b>License & Budget:</b> Open Source / Personal Project / ₹0 Initial Budget"))

        layout.addWidget(heading)
        layout.addWidget(card)
        layout.addStretch()
        return w

    # -------------------------------------------------------------------------
    # Credential & Provider Actions
    # -------------------------------------------------------------------------

    def _on_provider_selection_changed(self, index: int) -> None:
        provider_id = self.provider_combo.currentData()
        is_gemini = provider_id == "google_gemini"
        self.key_container.setVisible(is_gemini)
        if is_gemini:
            self._refresh_key_status()

    def _refresh_key_status(self) -> None:
        has_key = credentials.has_credential(GEMINI_KEY_NAME)
        if has_key:
            self.key_status_label.setText("🔒 API Key is securely stored in Windows Credential Manager")
            self.key_status_label.setStyleSheet(f"color: {STATUS_ONLINE}; font-weight: 600;")
        else:
            self.key_status_label.setText("⚠️ No API Key currently saved in Windows Credential Manager")
            self.key_status_label.setStyleSheet(f"color: {STATUS_WARNING}; font-weight: 600;")

    def _save_gemini_key(self) -> None:
        key = self.key_input.text().strip()
        if not key:
            self.test_result_label.setText("Please enter an API key to save.")
            self.test_result_label.setStyleSheet(f"color: {STATUS_WARNING};")
            return

        success = credentials.save_credential(GEMINI_KEY_NAME, key)
        if success:
            self.key_input.clear()
            self._refresh_key_status()
            self.test_result_label.setText("✓ Gemini API Key successfully saved into Windows Credential Manager.")
            self.test_result_label.setStyleSheet(f"color: {STATUS_ONLINE}; font-weight: 600;")
        else:
            self.test_result_label.setText("Failed to save key into Windows Credential Manager.")
            self.test_result_label.setStyleSheet(f"color: {STATUS_ERROR};")

    def _remove_gemini_key(self) -> None:
        credentials.delete_credential(GEMINI_KEY_NAME)
        self._refresh_key_status()
        self.test_result_label.setText("Key removed from Windows Credential Manager.")
        self.test_result_label.setStyleSheet(f"color: {TEXT_MUTED};")

    def _test_gemini_connection(self) -> None:
        provider = registry.get_provider("google_gemini")
        if not provider:
            self.test_result_label.setText("Gemini provider adapter not available.")
            self.test_result_label.setStyleSheet(f"color: {STATUS_ERROR};")
            return

        self.test_result_label.setText("⚡ Testing connection to Google Gemini...")
        self.test_result_label.setStyleSheet(f"color: {ACCENT_CYAN};")
        self.repaint()

        ok, msg = provider.test_connection()
        if ok:
            self.test_result_label.setText(f"✓ {msg}")
            self.test_result_label.setStyleSheet(f"color: {STATUS_ONLINE}; font-weight: 600;")
        else:
            self.test_result_label.setText(f"✕ {msg}")
            self.test_result_label.setStyleSheet(f"color: {STATUS_ERROR};")

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------

    def load_settings(self) -> None:
        """Load settings from SQLite database or fallback to defaults."""
        app_name = db.get_setting("app_name", config.app_name)
        wake_phrase = db.get_setting("wake_phrase", config.wake_phrase)
        active_provider_id = registry.get_active_provider_id()

        self.name_input.setText(app_name)
        self.wake_input.setText(wake_phrase)

        # Match provider combo
        idx = self.provider_combo.findData(active_provider_id)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        else:
            self.provider_combo.setCurrentIndex(0)

        self._on_provider_selection_changed(self.provider_combo.currentIndex())

    def save_settings(self) -> None:
        """Persist modified settings to SQLite."""
        db.set_setting("app_name", self.name_input.text().strip() or config.app_name)
        db.set_setting("wake_phrase", self.wake_input.text().strip() or config.wake_phrase)

        provider_id = self.provider_combo.currentData()
        registry.set_active_provider(provider_id)
        self.provider_changed.emit(provider_id)

        logger.info("Application settings and active provider saved to SQLite")
        self.feedback_label.setText("✓ Settings saved successfully")
