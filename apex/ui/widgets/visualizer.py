"""Visualizer widget for APEX: Minimal geometric 'A' core with ambient glow."""

import math
from PySide6.QtCore import QPointF, QRectF, QTimer, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget
from apex.ui.styles.palette import ACCENT_CYAN, ACCENT_PRIMARY, BG_DARK


class ApexVisualizer(QWidget):
    """Calm, futuristic geometric 'A' visualizer with breathing ambient glow."""

    def __init__(self, parent=None, size: int = 160):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._pulse_phase: float = 0.0
        self._state: str = "idle"  # idle, listening, thinking, speaking

        # Low-frequency 30 FPS pulse timer for battery/CPU efficiency on Core i3
        self._timer = QTimer(self)
        self._timer.setInterval(33)  # ~30 fps
        self._timer.timeout.connect(self._on_tick)
        self._timer.start()

    def set_state(self, state: str) -> None:
        """Update visualizer state: idle, listening, thinking, speaking."""
        self._state = state
        self.update()

    def _on_tick(self) -> None:
        # Subtle slow breathing pulse (period of ~3 seconds)
        self._pulse_phase += 0.04
        if self._pulse_phase > 2 * math.pi:
            self._pulse_phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        pulse = 0.5 + 0.5 * math.sin(self._pulse_phase)  # 0.0 to 1.0

        # Outer subtle ambient glow
        glow_radius = (self.width() / 2.0) * (0.75 + 0.15 * pulse)
        radial_grad = QRadialGradient(center_x, center_y, glow_radius)
        radial_grad.setColorAt(0.0, QColor(0, 217, 255, int(45 + 30 * pulse)))
        radial_grad.setColorAt(0.5, QColor(22, 139, 255, int(20 + 15 * pulse)))
        radial_grad.setColorAt(1.0, QColor(8, 11, 18, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(radial_grad))
        painter.drawEllipse(QPointF(center_x, center_y), glow_radius, glow_radius)

        # Concentric thin orbit rings
        pen_ring = QPen(QColor(0, 217, 255, int(30 + 20 * pulse)), 1.2)
        pen_ring.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen_ring)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(center_x, center_y), glow_radius * 0.85, glow_radius * 0.85)

        # Inner Geometric "A" Emblem
        # Triangle / Apex geometry
        scale = self.width() / 160.0
        top_vertex = QPointF(center_x, center_y - 36 * scale)
        bottom_left = QPointF(center_x - 30 * scale, center_y + 32 * scale)
        bottom_right = QPointF(center_x + 30 * scale, center_y + 32 * scale)

        a_path = QPainterPath()
        a_path.moveTo(top_vertex)
        a_path.lineTo(bottom_left)
        a_path.lineTo(bottom_right)
        a_path.closeSubpath()

        # Inner triangle cutout (chevron shape)
        inner_top = QPointF(center_x, center_y - 12 * scale)
        inner_left = QPointF(center_x - 14 * scale, center_y + 18 * scale)
        inner_right = QPointF(center_x + 14 * scale, center_y + 18 * scale)
        inner_path = QPainterPath()
        inner_path.moveTo(inner_top)
        inner_path.lineTo(inner_left)
        inner_path.lineTo(inner_right)
        inner_path.closeSubpath()

        a_shape = a_path.subtracted(inner_path)

        # Gradient fill for the emblem
        grad = QLinearGradient(top_vertex, QPointF(center_x, center_y + 32 * scale))
        grad.setColorAt(0.0, QColor(ACCENT_CYAN))
        grad.setColorAt(1.0, QColor(ACCENT_PRIMARY))

        painter.setPen(QPen(QColor(0, 217, 255, 180), 1.5))
        painter.setBrush(QBrush(grad))
        painter.drawPath(a_shape)

        # Subtle horizontal power line crossbar
        cross_pen = QPen(QColor(234, 241, 255, int(180 + 75 * pulse)), 2.0)
        painter.setPen(cross_pen)
        painter.drawLine(
            QPointF(center_x - 22 * scale, center_y + 10 * scale),
            QPointF(center_x + 22 * scale, center_y + 10 * scale),
        )
