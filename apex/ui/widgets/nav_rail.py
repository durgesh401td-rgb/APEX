"""Navigation rail widget for APEX."""

from typing import Callable, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from apex.ui.styles.palette import (
    ACCENT_CYAN,
    ACCENT_PRIMARY,
    BORDER_COLOR,
    STATUS_ONLINE,
    SURFACE_PRIMARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class NavRail(QWidget):
    """Left persistent navigation rail with clean icons and indicators."""

    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navRail")
        self.setFixedWidth(220)
        self._buttons: List[QPushButton] = []
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 20, 14, 18)
        layout.setSpacing(6)

        # Brand / Logo Header
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)

        title_label = QLabel("APEX")
        title_label.setStyleSheet(
            f"font-size: 20px; font-weight: 800; color: {TEXT_PRIMARY}; letter-spacing: 2px;"
        )
        tagline_label = QLabel("Think • Assist • Achieve")
        tagline_label.setStyleSheet(
            f"font-size: 10px; font-weight: 500; color: {TEXT_SECONDARY}; text-transform: uppercase;"
        )

        brand_layout.addWidget(title_label)
        brand_layout.addWidget(tagline_label)
        layout.addLayout(brand_layout)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Plain)
        divider.setStyleSheet(f"background-color: {BORDER_COLOR}; height: 1px; margin-top: 10px; margin-bottom: 12px;")
        layout.addWidget(divider)

        # Navigation Items: (Title, Icon Symbol, Page Index)
        nav_items = [
            ("Home", "⚡", 0),
            ("Chat", "💬", 1),
            ("Tools", "🛠️", 2),
            ("Automation", "⚙️", 3),
            ("Files", "📁", 4),
            ("Memory", "🧠", 5),
            ("Devices", "📱", 6),
            ("Settings", "🔧", 7),
        ]

        for title, icon, index in nav_items:
            btn = QPushButton(f"  {icon}   {title}")
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if index == 0:
                btn.setChecked(True)

            self._button_group.addButton(btn, index)
            self._buttons.append(btn)
            layout.addWidget(btn)

        self._button_group.idClicked.connect(self._on_button_clicked)

        # Spacer to push status to bottom
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Bottom System Status Widget
        status_box = QFrame()
        status_box.setStyleSheet(
            f"background-color: #0E1522; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 10px;"
        )
        status_layout = QVBoxLayout(status_box)
        status_layout.setContentsMargins(6, 6, 6, 6)
        status_layout.setSpacing(4)

        status_header = QHBoxLayout()
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {STATUS_ONLINE}; font-size: 10px;")
        status_title = QLabel("System Ready")
        status_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11px; font-weight: 600;")
        status_header.addWidget(status_dot)
        status_header.addWidget(status_title)
        status_header.addStretch()

        status_detail = QLabel("Local Engine • v0.1.0")
        status_detail.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px;")

        status_layout.addLayout(status_header)
        status_layout.addWidget(status_detail)
        layout.addWidget(status_box)

    def _on_button_clicked(self, page_index: int) -> None:
        self.page_changed.emit(page_index)

    def set_active_page(self, page_index: int) -> None:
        btn = self._button_group.button(page_index)
        if btn:
            btn.setChecked(True)
