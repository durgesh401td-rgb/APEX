"""User Memory Vault page for APEX: Inspect, edit, pause, and delete memories."""

from datetime import datetime
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from apex.core.memory import memory_service
from apex.ui.styles.palette import (
    ACCENT_CYAN,
    ACCENT_PRIMARY,
    BORDER_COLOR,
    STATUS_ERROR,
    STATUS_ONLINE,
    STATUS_WARNING,
    SURFACE_ELEVATED,
    SURFACE_HOVER,
    SURFACE_PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class AddEditMemoryDialog(QDialog):
    """Dialog to create or edit a memory item."""

    def __init__(self, content: str = "", category: str = "preference", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Memory" if content else "Add to Memory Vault")
        self.setFixedWidth(460)
        self.setStyleSheet(f"background-color: {SURFACE_PRIMARY}; color: {TEXT_PRIMARY};")
        self._init_ui(content, category)

    def _init_ui(self, content: str, category: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_lbl = QLabel("Memory Details")
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(title_lbl)

        layout.addWidget(QLabel("Category:"))
        self.cat_combo = QComboBox()
        self.cat_combo.setStyleSheet(
            f"background-color: {SURFACE_ELEVATED}; color: {TEXT_PRIMARY}; padding: 6px 10px; border: 1px solid {BORDER_COLOR}; border-radius: 6px;"
        )
        self.cat_combo.addItems(["preference", "fact", "profile", "project", "general"])
        idx = self.cat_combo.findText(category.lower())
        if idx >= 0:
            self.cat_combo.setCurrentIndex(idx)
        layout.addWidget(self.cat_combo)

        layout.addWidget(QLabel("Content (Information to remember):"))
        self.content_edit = QTextEdit()
        self.content_edit.setText(content)
        self.content_edit.setPlaceholderText("e.g. Prefers concise code snippets without unnecessary commentary...")
        self.content_edit.setMinimumHeight(100)
        layout.addWidget(self.content_edit)

        # Buttons
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_data(self) -> tuple[str, str]:
        return self.content_edit.toPlainText().strip(), self.cat_combo.currentText().lower()


class MemoryCard(QFrame):
    """Card widget representing an individual memory."""

    edit_requested = Signal(dict)
    delete_requested = Signal(str)

    def __init__(self, memory_data: dict, parent=None):
        super().__init__(parent)
        self.data = memory_data
        self._init_ui()

    def _init_ui(self) -> None:
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {SURFACE_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: #2B4263;
            }}
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        # Header: category badge + timestamp + actions
        header = QHBoxLayout()

        category = self.data.get("category", "general").capitalize()
        cat_badge = QLabel(category)
        cat_badge.setStyleSheet(
            f"""
            background-color: rgba(22, 139, 255, 0.12);
            color: {ACCENT_CYAN};
            border: 1px solid rgba(0, 217, 255, 0.25);
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 600;
            """
        )
        header.addWidget(cat_badge)

        created_at = self.data.get("updated_at", "")
        time_text = created_at.split("T")[0] if "T" in created_at else created_at
        time_lbl = QLabel(time_text)
        time_lbl.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; margin-left: 8px;")
        header.addWidget(time_lbl)

        header.addStretch()

        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setProperty("class", "secondary-btn")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.data))
        header.addWidget(edit_btn)

        del_btn = QPushButton("🗑️")
        del_btn.setToolTip("Delete memory")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(
            f"background: transparent; border: none; color: {STATUS_ERROR}; font-size: 14px; padding: 4px;"
        )
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.data["id"]))
        header.addWidget(del_btn)

        layout.addLayout(header)

        # Content
        content_lbl = QLabel(self.data.get("content", ""))
        content_lbl.setWordWrap(True)
        content_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_lbl.setStyleSheet(
            f"font-size: 13px; color: {TEXT_PRIMARY}; line-height: 1.4; background: transparent; border: none;"
        )
        layout.addWidget(content_lbl)


class MemoryPage(QWidget):
    """User Memory Vault management workspace."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.refresh_memories()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # Top Header & Pause Toggle
        header_row = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_lbl = QLabel("User Memory Vault")
        title_lbl.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {TEXT_PRIMARY};")
        subtitle_lbl = QLabel("Explicit, user-approved long-term knowledge, preferences, and facts.")
        subtitle_lbl.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY};")
        title_col.addWidget(title_lbl)
        title_col.addWidget(subtitle_lbl)
        header_row.addLayout(title_col)

        header_row.addStretch()

        # Pause / Active Button
        self.pause_btn = QPushButton()
        self.pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pause_btn.clicked.connect(self._toggle_pause_state)
        header_row.addWidget(self.pause_btn)

        add_btn = QPushButton("➕  Add Fact")
        add_btn.setProperty("class", "action-btn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_memory_dialog)
        header_row.addWidget(add_btn)

        main_layout.addLayout(header_row)

        # Filter & Search Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search memories by keyword...")
        self.search_input.textChanged.connect(self.refresh_memories)
        toolbar.addWidget(self.search_input)

        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(
            f"background-color: {SURFACE_PRIMARY}; color: {TEXT_PRIMARY}; padding: 8px 12px; border: 1px solid {BORDER_COLOR}; border-radius: 8px;"
        )
        self.category_combo.addItems(["All Categories", "Preference", "Fact", "Profile", "Project", "General"])
        self.category_combo.currentIndexChanged.connect(self.refresh_memories)
        toolbar.addWidget(self.category_combo)

        clear_all_btn = QPushButton("Clear Vault")
        clear_all_btn.setProperty("class", "secondary-btn")
        clear_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_all_btn.clicked.connect(self._clear_all_dialog)
        toolbar.addWidget(clear_all_btn)

        main_layout.addLayout(toolbar)

        # Scrollable Memory Cards Container
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 8, 0, 8)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area)

        self._update_pause_button_ui()

    # -------------------------------------------------------------------------
    # State & Refresh
    # -------------------------------------------------------------------------

    def _update_pause_button_ui(self) -> None:
        paused = memory_service.is_paused()
        if paused:
            self.pause_btn.setText("⏸  Memory Paused")
            self.pause_btn.setStyleSheet(
                f"background-color: rgba(245, 158, 11, 0.15); color: {STATUS_WARNING}; border: 1px solid {STATUS_WARNING}; border-radius: 8px; padding: 10px 16px; font-weight: 600;"
            )
        else:
            self.pause_btn.setText("✔  Memory Active")
            self.pause_btn.setStyleSheet(
                f"background-color: rgba(16, 185, 129, 0.15); color: {STATUS_ONLINE}; border: 1px solid {STATUS_ONLINE}; border-radius: 8px; padding: 10px 16px; font-weight: 600;"
            )

    def _toggle_pause_state(self) -> None:
        new_state = not memory_service.is_paused()
        memory_service.set_paused(new_state)
        self._update_pause_button_ui()

    def refresh_memories(self) -> None:
        """Fetch filtered memories and render cards."""
        # Clear existing cards
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        search_text = self.search_input.text().strip()
        cat_text = self.category_combo.currentText().lower()
        category = None if cat_text.startswith("all") else cat_text

        memories = memory_service.list_memories(search_query=search_text, category=category)

        if not memories:
            empty_card = QFrame()
            empty_card.setStyleSheet(
                f"background-color: {SURFACE_PRIMARY}; border: 1px dashed {BORDER_COLOR}; border-radius: 12px; padding: 30px;"
            )
            empty_layout = QVBoxLayout(empty_card)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl = QLabel("🧠 No stored memories match your search.")
            lbl.setStyleSheet(f"font-size: 14px; color: {TEXT_MUTED};")
            empty_layout.addWidget(lbl)
            self.cards_layout.insertWidget(0, empty_card)
            return

        for m in memories:
            card = MemoryCard(m)
            card.edit_requested.connect(self._edit_memory_dialog)
            card.delete_requested.connect(self._delete_memory)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    # -------------------------------------------------------------------------
    # Dialogs & CRUD
    # -------------------------------------------------------------------------

    def _add_memory_dialog(self) -> None:
        dlg = AddEditMemoryDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            content, cat = dlg.get_data()
            if content:
                memory_service.add_memory(content=content, category=cat)
                self.refresh_memories()

    def _edit_memory_dialog(self, memory_data: dict) -> None:
        dlg = AddEditMemoryDialog(
            content=memory_data.get("content", ""),
            category=memory_data.get("category", "preference"),
            parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            content, cat = dlg.get_data()
            if content:
                memory_service.update_memory(
                    memory_id=memory_data["id"],
                    new_content=content,
                    new_category=cat,
                )
                self.refresh_memories()

    def _delete_memory(self, memory_id: str) -> None:
        reply = QMessageBox.question(
            self,
            "Delete Memory",
            "Are you sure you want to delete this memory?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            memory_service.delete_memory(memory_id)
            self.refresh_memories()

    def _clear_all_dialog(self) -> None:
        reply = QMessageBox.warning(
            self,
            "Clear Entire Vault",
            "Are you sure you want to permanently delete ALL saved memories?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            memory_service.clear_all()
            self.refresh_memories()
