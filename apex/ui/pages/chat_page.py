"""Chat workspace page for APEX with asynchronous AI provider integration."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from PySide6.QtCore import Qt, QThread, QTimer, Signal
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
from apex.core.memory import memory_service
from apex.core.providers.base import BaseAIProvider, ProviderResponse
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
from apex.ui.widgets.chat_bubble import ChatBubble


class AIWorkerThread(QThread):
    """Background worker executing model inference without blocking the UI."""

    response_ready = Signal(object)  # ProviderResponse
    failed = Signal(str)

    def __init__(
        self,
        provider: BaseAIProvider,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.provider = provider
        self.messages = messages
        self.system_prompt = system_prompt
        self._is_cancelled = False

    def cancel(self) -> None:
        self._is_cancelled = True

    def run(self) -> None:
        try:
            resp = self.provider.generate(self.messages, system_prompt=self.system_prompt)
            if not self._is_cancelled:
                self.response_ready.emit(resp)
        except Exception as e:
            if not self._is_cancelled:
                self.failed.emit(str(e))


class ChatPage(QWidget):
    """Dedicated conversation workspace with history drawer, message canvas, and composer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_conv_id: Optional[str] = None
        self.ai_worker: Optional[AIWorkerThread] = None
        self._init_ui()
        self.load_conversations()
        self.refresh_provider_pill()

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
        self.provider_pill = QLabel("Offline Mock Assistant")
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
        # Canonical Qt auto-scroll: automatically track bottom when new content is added
        self.scroll_area.verticalScrollBar().rangeChanged.connect(
            lambda min_val, max_val: self.scroll_area.verticalScrollBar().setValue(max_val)
        )
        chat_layout.addWidget(self.scroll_area)

        # Typing / Thinking Indicator (hidden by default)
        indicator_row = QHBoxLayout()
        self.thinking_label = QLabel("⚡ APEX is thinking...")
        self.thinking_label.setStyleSheet(
            f"font-size: 12px; color: {ACCENT_CYAN}; padding-left: 12px; font-style: italic;"
        )
        self.thinking_label.setVisible(False)

        self.stop_btn = QPushButton("⏹  Stop Generation")
        self.stop_btn.setProperty("class", "secondary-btn")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setVisible(False)
        self.stop_btn.clicked.connect(self.cancel_generation)

        indicator_row.addWidget(self.thinking_label)
        indicator_row.addStretch()
        indicator_row.addWidget(self.stop_btn)
        chat_layout.addLayout(indicator_row)

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
    # Provider & UI Helpers
    # -------------------------------------------------------------------------

    def refresh_provider_pill(self, provider_id: Optional[str] = None) -> None:
        """Update top-right badge reflecting active model provider."""
        provider = registry.get_active_provider()
        self.provider_pill.setText(f"⚡ {provider.display_name}")

    # -------------------------------------------------------------------------
    # Conversation Logic
    # -------------------------------------------------------------------------

    def load_conversations(self) -> None:
        """Load conversation list from SQLite."""
        self.conv_list_widget.clear()
        convs = db.list_conversations()
        if not convs:
            self.start_new_conversation("Welcome to APEX")
            return

        for conv in convs:
            item = QListWidgetItem(conv["title"])
            item.setData(Qt.ItemDataRole.UserRole, conv["id"])
            self.conv_list_widget.addItem(item)

        first_item = self.conv_list_widget.item(0)
        if first_item:
            self.conv_list_widget.setCurrentItem(first_item)
            self._switch_conversation(first_item.data(Qt.ItemDataRole.UserRole), first_item.text())

    def start_new_conversation(self, title: str = "New Conversation") -> None:
        """Create a new conversation session."""
        conv_id = db.create_conversation(title=title)
        
        provider = registry.get_active_provider()
        welcome_text = (
            f"Hello! I am APEX, powered by {provider.display_name}. "
            "How can I assist your workflow today?"
        )
        db.add_message(conv_id, "assistant", welcome_text)

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

    # -------------------------------------------------------------------------
    # Asynchronous Message Sending & Cancellation
    # -------------------------------------------------------------------------

    def send_message(self) -> None:
        """Send user message and dispatch async inference to active AI provider."""
        text = self.message_input.text().strip()
        if not text or not self.active_conv_id:
            return

        self.message_input.clear()
        now = datetime.now(timezone.utc).isoformat()

        # Add user message to DB and UI
        db.add_message(self.active_conv_id, "user", text)
        user_bubble = ChatBubble(role="user", content=text, timestamp=now)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, user_bubble)

        # Auto-title conversation on first user query
        messages = db.get_messages(self.active_conv_id)
        if len(messages) == 2 and messages[0]["role"] == "assistant":
            new_title = text[:28] + ("..." if len(text) > 28 else "")
            db.update_conversation_title(self.active_conv_id, new_title)
            self.conv_title_label.setText(new_title)
            current_item = self.conv_list_widget.currentItem()
            if current_item:
                current_item.setText(new_title)

        self._scroll_to_bottom()

        # Update UI state for background processing
        provider = registry.get_active_provider()
        self.thinking_label.setText(f"⚡ Connecting to {provider.display_name}...")
        self.thinking_label.setVisible(True)
        self.stop_btn.setVisible(True)
        self.send_btn.setEnabled(False)

        # Explicit user memory saving check (never silent)
        text_lower = text.lower()
        if text_lower.startswith("remember:") or text_lower.startswith("remember that "):
            fact = text.split(":", 1)[1].strip() if ":" in text else text[14:].strip()
            if fact:
                memory_service.add_memory(fact, category="fact")
                logger.info("Explicit memory saved from chat command: %s", fact[:30])

        # Prepare context history
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ]

        # Inject long-term memory context into system instruction if enabled
        system_prompt = "You are APEX, a helpful, precise personal AI assistant for Windows."
        memory_context = memory_service.get_context_for_prompt()
        if memory_context:
            system_prompt += f"\n\n{memory_context}"

        self.ai_worker = AIWorkerThread(provider, history, system_prompt=system_prompt, parent=self)
        self.ai_worker.response_ready.connect(self._on_ai_response)
        self.ai_worker.failed.connect(self._on_ai_failure)
        self.ai_worker.start()

    def cancel_generation(self) -> None:
        """Cancel ongoing AI worker thread."""
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.cancel()
            self.ai_worker.wait(500)

            now = datetime.now(timezone.utc).isoformat()
            cancel_msg = "*(Generation cancelled by user)*"
            if self.active_conv_id:
                db.add_message(self.active_conv_id, "assistant", cancel_msg)
            assistant_bubble = ChatBubble(role="assistant", content=cancel_msg, timestamp=now)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, assistant_bubble)
            self._scroll_to_bottom()

        self._reset_composer_state()

    def closeEvent(self, event) -> None:
        """Ensure background threads are safely terminated upon page closure."""
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.cancel()
            self.ai_worker.wait(500)
        super().closeEvent(event)

    def _on_ai_response(self, response: ProviderResponse) -> None:
        """Handle successful response from background AI worker."""
        self._reset_composer_state()
        if not self.active_conv_id:
            return

        now = datetime.now(timezone.utc).isoformat()
        db.add_message(self.active_conv_id, "assistant", response.content)
        assistant_bubble = ChatBubble(role="assistant", content=response.content, timestamp=now)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, assistant_bubble)
        self._scroll_to_bottom()

    def _on_ai_failure(self, error_message: str) -> None:
        """Handle error from background AI worker."""
        self._reset_composer_state()
        if not self.active_conv_id:
            return

        now = datetime.now(timezone.utc).isoformat()
        err_text = f"⚠️ Error: {error_message}"
        db.add_message(self.active_conv_id, "assistant", err_text)
        assistant_bubble = ChatBubble(role="assistant", content=err_text, timestamp=now)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, assistant_bubble)
        self._scroll_to_bottom()

    def _reset_composer_state(self) -> None:
        self.thinking_label.setVisible(False)
        self.stop_btn.setVisible(False)
        self.send_btn.setEnabled(True)

    def _scroll_to_bottom(self) -> None:
        """No-op as scroll tracking is automatically handled by scrollBar.rangeChanged."""
        pass
