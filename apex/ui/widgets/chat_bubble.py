"""Chat bubble widget displaying user or assistant messages."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
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


class ChatBubble(QWidget):
    """Render a styled conversation bubble for user or assistant."""

    def __init__(self, role: str, content: str, timestamp: str = "", parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self._init_ui()

    def _init_ui(self) -> None:
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 4, 0, 4)

        is_user = self.role == "user"

        card = QFrame()
        card.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(6)

        if is_user:
            # User styling: aligned right, elevated surface with electric blue accent border
            card.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {SURFACE_ELEVATED};
                    border: 1px solid #1E3A5F;
                    border-radius: 14px;
                    border-bottom-right-radius: 4px;
                }}
                """
            )
            outer_layout.addStretch()
            outer_layout.addWidget(card)
        else:
            # Assistant styling: aligned left, graphite surface with subtle cyan accent border
            card.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {SURFACE_PRIMARY};
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 14px;
                    border-bottom-left-radius: 4px;
                }}
                """
            )
            outer_layout.addWidget(card)
            outer_layout.addStretch()

        # Header with role title & timestamp
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        role_label = QLabel("You" if is_user else "APEX")
        if is_user:
            role_label.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {ACCENT_PRIMARY};")
        else:
            role_label.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {ACCENT_CYAN};")

        header_layout.addWidget(role_label)

        if self.timestamp:
            # Clean up ISO timestamp for display
            time_display = self.timestamp.split("T")[-1][:5] if "T" in self.timestamp else self.timestamp
            time_label = QLabel(time_display)
            time_label.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED};")
            header_layout.addWidget(time_label)

        header_layout.addStretch()
        card_layout.addLayout(header_layout)

        # Message Body
        msg_label = QLabel(self.content)
        msg_label.setWordWrap(True)
        msg_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        msg_label.setStyleSheet(
            f"font-size: 13px; line-height: 1.4; color: {TEXT_PRIMARY}; background: transparent; border: none;"
        )
        msg_label.setMaximumWidth(680)

        card_layout.addWidget(msg_label)
