"""Placeholder page for roadmap milestones in later stages."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget
from apex.ui.styles.palette import (
    ACCENT_CYAN,
    ACCENT_PRIMARY,
    BORDER_COLOR,
    SURFACE_PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class PlaceholderPage(QWidget):
    """Clean placeholder page describing upcoming roadmap capability."""

    def __init__(self, title: str, description: str, stage_tag: str, icon: str = "⚡", parent=None):
        super().__init__(parent)
        self._init_ui(title, description, stage_tag, icon)

    def _init_ui(self, title: str, description: str, stage_tag: str, icon: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setMaximumWidth(560)
        card.setStyleSheet(
            f"""
            background-color: {SURFACE_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 16px;
            padding: 30px;
            """
        )
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 40px; color: {ACCENT_CYAN};")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY};")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        stage_pill = QLabel(f"Scheduled for {stage_tag}")
        stage_pill.setStyleSheet(
            f"""
            background-color: rgba(22, 139, 255, 0.12);
            color: {ACCENT_PRIMARY};
            border: 1px solid rgba(22, 139, 255, 0.3);
            border-radius: 12px;
            padding: 4px 14px;
            font-size: 11px;
            font-weight: 600;
            """
        )
        stage_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_lbl = QLabel(description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(
            f"font-size: 13px; color: {TEXT_SECONDARY}; line-height: 1.5; margin-top: 8px;"
        )
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(icon_lbl)
        card_layout.addWidget(title_lbl)
        card_layout.addWidget(stage_pill)
        card_layout.addWidget(desc_lbl)

        layout.addWidget(card)
