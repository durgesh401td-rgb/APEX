"""Chat workspace page for APEX."""

from datetime import datetime, timezone
from typing import Optional
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from apex.core.database import db
from apex.core.logging import logger
from apex.ui.styles.palette import (
    ACCENT_CYAN,
    ACCENT_PRIMARY,
    BORDER_COLOR,
    SURFACE_ELEVATED,
    SURFACE_PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from apex.ui.widgets.chat_bubble import ChatBubble


class ChatPage(QWidget):
    """Dedicated conversation workspace with history drawer, message canvas, and composer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_conv_id: Optional[str] = None
        self._init_ui()
        self.load_conversations()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter between history sidebar and message area
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {BORDER_COLOR}; }}")

        # ---------------------------------------------------------------------
        # Left Conversation Drawer
        # ---------------------------------------------------------------------
        history_panel = QFrame()
        history_panel.setMinimumWidth(220)
        history_panel.setMaximumWidth(280)
        history_panel.setStyleSheet(
            f"background-color: {SURFACE_PRIMARY}; border-right: 1px solid {BORDER_COLOR};"
        )
        history_layout = QVBoxLayout(history_panel)
        history_layout.setContentsMargins(14, 16, 14, 16)
        history_layout.setSpacing(10)

        # "New Chat" button
        new_chat_btn = QPushButton("➕   New Conversation")
        new_chat_btn.setProperty("class", "action-btn")
        new_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_chat_btn.clicked.connect(self.start_new_conversation)
        history_layout.addWidget(new_chat_btn)

        history_label = QLabel("Recent Chats")
        history_label.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {TEXT_MUTED}; text-transform: uppercase; margin-top: 8px;"
        )
        history_layout.addWidget(history_label)

        # Conversation List
        self.conv_list_widget = QListWidget()
        self.conv_list_widget.setStyleSheet(
            f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-radius: 8px;
                color: {TEXT_SECONDARY};
                font-size: 13px;
                margin-bottom: 2px;
            }}
            QListWidget::item:hover {{
                background-color: {SURFACE_ELEVATED};
                color: {TEXT_PRIMARY};
            }}
            QListWidget::item:selected {{
                background-color: {SURFACE_ELEVATED};
                color: {ACCENT_CYAN};
                font-weight: 600;
                border-left: 3px solid {ACCENT_PRIMARY};
            }}
            """
        )
        self.conv_list_widget.itemClicked.connect(self._on_conv_selected)
        history_layout.addWidget(self.conv_list_widget)

        splitter.addWidget(history_panel)

        # ---------------------------------------------------------------------
        # Right Chat Canvas & Composer
        # ---------------------------------------------------------------------
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(28, 20, 28, 20)
        chat_layout.setSpacing(14)

        # Chat Top Bar
        top_bar = QHBoxLayout()
        self.conv_title_label = QLabel("Conversation")
        self.conv_title_label.setStyleSheet(
            f"font-size: 17px; font-weight: 700; color: {TEXT_PRIMARY};"
        )
        self.provider_pill = QLabel("Mock AI (Stage 1)")
        self.provider_pill.setStyleSheet(
            f"""
            background-color: rgba(22, 139, 255, 0.12);
            color: {ACCENT_CYAN};
            border: 1px solid rgba(0, 217, 255, 0.25);
            border-radius: 12px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 600;
            """
        )
        top_bar.addWidget(self.conv_title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.provider_pill)
        chat_layout.addLayout(top_bar)

        # Messages Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.messages_container = QWidget()
        self.messages_container.setStyleSheet("background: transparent;")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.setSpacing(12)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_container)
        chat_layout.addWidget(self.scroll_area)

        # Typing / Thinking Indicator (hidden by default)
        self.thinking_label = QLabel("⚡ APEX is processing response...")
        self.thinking_label.setStyleSheet(
            f"font-size: 12px; color: {ACCENT_CYAN}; padding-left: 12px; font-style: italic;"
        )
        self.thinking_label.setVisible(False)
        chat_layout.addWidget(self.thinking_label)

        # Composer Box
        composer_frame = QFrame()
        composer_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {SURFACE_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 14px;
                padding: 4px;
            }}
            """
        )
        composer_layout = QHBoxLayout(composer_frame)
        composer_layout.setContentsMargins(10, 4, 10, 4)
        composer_layout.setSpacing(8)

        # Attach placeholder button
        attach_btn = QPushButton("📎")
        attach_btn.setFixedSize(36, 36)
        attach_btn.setToolTip("Attach file or image (Stage 7)")
        attach_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        attach_btn.setStyleSheet(
            f"background: transparent; border: none; font-size: 16px; color: {TEXT_MUTED};"
        )

        # Text input
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask APEX anything... (Press Enter to send)")
        self.message_input.setStyleSheet(
            f"background: transparent; border: none; font-size: 14px; color: {TEXT_PRIMARY}; padding: 8px 4px;"
        )
        self.message_input.returnPressed.connect(self.send_message)

        # Voice placeholder button
        voice_btn = QPushButton("🎙️")
        voice_btn.setFixedSize(36, 36)
        voice_btn.setToolTip("Voice input / Push-to-talk (Stage 4)")
        voice_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        voice_btn.setStyleSheet(
            f"background: transparent; border: none; font-size: 16px; color: {TEXT_MUTED};"
        )

        # Send Button
        self.send_btn = QPushButton("Send")
        self.send_btn.setProperty("class", "action-btn")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.clicked.connect(self.send_message)

        composer_layout.addWidget(attach_btn)
        composer_layout.addWidget(self.message_input)
        composer_layout.addWidget(voice_btn)
        composer_layout.addWidget(self.send_btn)

        chat_layout.addWidget(composer_frame)

        splitter.addWidget(chat_area)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    # -------------------------------------------------------------------------
    # Conversation Logic
    # -------------------------------------------------------------------------

    def load_conversations(self) -> None:
        """Load conversation list from SQLite."""
        self.conv_list_widget.clear()
        convs = db.list_conversations()
        if not convs:
            # Create first welcome chat
            self.start_new_conversation("Welcome to APEX")
            return

        for conv in convs:
            item = QListWidgetItem(conv["title"])
            item.setData(Qt.ItemDataRole.UserRole, conv["id"])
            self.conv_list_widget.addItem(item)

        # Select first conversation by default
        first_item = self.conv_list_widget.item(0)
        if first_item:
            self.conv_list_widget.setCurrentItem(first_item)
            self._switch_conversation(first_item.data(Qt.ItemDataRole.UserRole), first_item.text())

    def start_new_conversation(self, title: str = "New Conversation") -> None:
        """Create a new conversation session."""
        conv_id = db.create_conversation(title=title)
        
        # Add welcome intro message from APEX
        welcome_text = (
            "Hello! I am APEX, your personal assistant. Stage 1 desktop environment "
            "and local persistence are active. How can I help you today?"
        )
        db.add_message(conv_id, "assistant", welcome_text)

        # Reload list and select new chat
        self.conv_list_widget.clear()
        convs = db.list_conversations()
        for conv in convs:
            item = QListWidgetItem(conv["title"])
            item.setData(Qt.ItemDataRole.UserRole, conv["id"])
            self.conv_list_widget.addItem(item)
            if conv["id"] == conv_id:
                self.conv_list_widget.setCurrentItem(item)

        self._switch_conversation(conv_id, title)

    def _on_conv_selected(self, item: QListWidgetItem) -> None:
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        self._switch_conversation(conv_id, item.text())

    def _switch_conversation(self, conv_id: str, title: str) -> None:
        self.active_conv_id = conv_id
        self.conv_title_label.setText(title)
        self._load_messages_for_active_conv()

    def _load_messages_for_active_conv(self) -> None:
        """Clear message viewport and load messages from SQLite."""
        # Clear existing bubbles
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.active_conv_id:
            return

        messages = db.get_messages(self.active_conv_id)
        for msg in messages:
            bubble = ChatBubble(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)

        self._scroll_to_bottom()

    def send_message(self) -> None:
        """Send user message, persist to SQLite, and generate mock assistant response."""
        text = self.message_input.text().strip()
        if not text or not self.active_conv_id:
            return

        self.message_input.clear()
        now = datetime.now(timezone.utc).isoformat()

        # Add user message to SQLite and UI
        db.add_message(self.active_conv_id, "user", text)
        user_bubble = ChatBubble(role="user", content=text, timestamp=now)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, user_bubble)

        # Update conversation title if first message
        messages = db.get_messages(self.active_conv_id)
        if len(messages) == 2 and messages[0]["role"] == "assistant":
            # Auto-title conversation from first user query
            new_title = text[:28] + ("..." if len(text) > 28 else "")
            db.update_conversation_title(self.active_conv_id, new_title)
            self.conv_title_label.setText(new_title)
            current_item = self.conv_list_widget.currentItem()
            if current_item:
                current_item.setText(new_title)

        self._scroll_to_bottom()

        # Show simulated thinking state
        self.thinking_label.setVisible(True)
        self.send_btn.setEnabled(False)

        # Simulate local response after 600ms safely
        def safe_reply():
            try:
                self._generate_mock_response(text)
            except RuntimeError:
                pass

        QTimer.singleShot(600, safe_reply)

    def _generate_mock_response(self, user_query: str) -> None:
        """Generate intelligent mock response demonstrating complete offline loop."""
        try:
            self.thinking_label.setVisible(False)
            self.send_btn.setEnabled(True)

            if not self.active_conv_id:
                return

            # Simple keyword matching to simulate useful local responses
            query_lower = user_query.lower()
            if "hello" in query_lower or "hi" in query_lower:
                reply = "Greetings! APEX desktop is running in Stage 1 offline mode. All messages are securely saved to your local SQLite database."
            elif "status" in query_lower or "system" in query_lower:
                reply = "System Status: Nominal. Process running on Intel Core i3 with 8 GB RAM optimization. No cloud network dependencies currently active."
            elif "roadmap" in query_lower or "stage" in query_lower:
                reply = "Currently on Stage 1 (Core Desktop). Stage 2 will introduce the cloud AI provider adapter (Google Gemini / OpenAI / Ollama)."
            else:
                reply = f"Acknowledged: \"{user_query}\". Stage 1 desktop shell and SQLite persistence verified. Cloud AI reasoning will connect in Stage 2."

            now = datetime.now(timezone.utc).isoformat()
            db.add_message(self.active_conv_id, "assistant", reply)
            assistant_bubble = ChatBubble(role="assistant", content=reply, timestamp=now)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, assistant_bubble)
            self._scroll_to_bottom()
        except RuntimeError:
            pass

    def _scroll_to_bottom(self) -> None:
        def do_scroll():
            try:
                if hasattr(self, "scroll_area") and self.scroll_area:
                    bar = self.scroll_area.verticalScrollBar()
                    if bar:
                        bar.setValue(bar.maximum())
            except (RuntimeError, AttributeError):
                pass

        QTimer.singleShot(50, do_scroll)
