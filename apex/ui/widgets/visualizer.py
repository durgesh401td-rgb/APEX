"""Visualizer widget for APEX: Minimal geometric 'A' core with dynamic voice states."""

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
from apex.core.voice.state import voice_state
from apex.ui.styles.palette import ACCENT_CYAN, ACCENT_PRIMARY, STATUS_ERROR, STATUS_ONLINE, TEXT_MUTED


class ApexVisualizer(QWidget):
    """Calm, futuristic geometric 'A' visualizer with reactive voice states."""

    def __init__(self, parent=None, size: int = 160):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._pulse_phase: float = 0.0
        self._rotation_angle: float = 0.0
        self._state: str = "idle"  # idle, listening, thinking, speaking, muted

        # 30 FPS pulse timer for battery/CPU efficiency on Core i3
        self._timer = QTimer(self)
        self._timer.setInterval(33)  # ~30 fps
        self._timer.timeout.connect(self._on_tick)
        self._timer.start()

        # Connect voice state observer and cleanup on destruction
        voice_state.add_listener(self._on_voice_state_event)
        self.destroyed.connect(lambda: voice_state.remove_listener(self._on_voice_state_event))

    def _on_voice_state_event(self, event: str, value: bool) -> None:
        try:
            if event == "listening":
                self.set_state("listening" if value else "idle")
            elif event == "speaking":
                self.set_state("speaking" if value else "idle")
            elif event == "muted":
                if value:
                    self.set_state("muted")
                elif self._state == "muted":
                    self.set_state("idle")
        except RuntimeError:
            pass

    def set_state(self, state: str) -> None:
        """Update visualizer state: idle, listening, thinking, speaking, muted."""
        self._state = state
        self.update()

    def _on_tick(self) -> None:
        speed = 0.04
        if self._state == "listening":
            speed = 0.12  # Faster pulse for listening
        elif self._state == "thinking":
            speed = 0.08
            self._rotation_angle = (self._rotation_angle + 3.0) % 360
        elif self._state == "speaking":
            speed = 0.10  # Audio reactive modulation

        self._pulse_phase += speed
        if self._pulse_phase > 2 * math.pi:
            self._pulse_phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        pulse = 0.5 + 0.5 * math.sin(self._pulse_phase)

        scale = self.width() / 160.0

        # Color schemes depending on state
        if self._state == "listening":
            glow_c1 = QColor(0, 217, 255, int(90 + 60 * pulse))
            glow_c2 = QColor(22, 139, 255, int(50 + 30 * pulse))
            ring_pen = QPen(QColor(0, 217, 255, int(120 + 80 * pulse)), 2.0)
            status_text = "LISTENING"
            accent_c = ACCENT_CYAN
        elif self._state == "thinking":
            glow_c1 = QColor(22, 139, 255, int(70 + 40 * pulse))
            glow_c2 = QColor(140, 60, 255, int(40 + 20 * pulse))
            ring_pen = QPen(QColor(140, 60, 255, int(100 + 50 * pulse)), 1.5)
            ring_pen.setStyle(Qt.PenStyle.DashDotLine)
            status_text = "THINKING"
            accent_c = ACCENT_PRIMARY
        elif self._state == "speaking":
            glow_c1 = QColor(16, 185, 129, int(80 + 50 * pulse))
            glow_c2 = QColor(0, 217, 255, int(40 + 30 * pulse))
            ring_pen = QPen(QColor(16, 185, 129, int(120 + 60 * pulse)), 2.2)
            status_text = "SPEAKING"
            accent_c = STATUS_ONLINE
        elif self._state == "muted":
            glow_c1 = QColor(100, 116, 139, 25)
            glow_c2 = QColor(30, 41, 59, 10)
            ring_pen = QPen(QColor(100, 116, 139, 40), 1.0)
            status_text = "MUTED"
            accent_c = TEXT_MUTED
        else:  # idle
            glow_c1 = QColor(0, 217, 255, int(45 + 30 * pulse))
            glow_c2 = QColor(22, 139, 255, int(20 + 15 * pulse))
            ring_pen = QPen(QColor(0, 217, 255, int(30 + 20 * pulse)), 1.2)
            ring_pen.setStyle(Qt.PenStyle.DashLine)
            status_text = ""
            accent_c = ACCENT_CYAN

        # Ambient radial glow
        glow_radius = (self.width() / 2.0) * (0.75 + 0.15 * pulse)
        radial_grad = QRadialGradient(center_x, center_y, glow_radius)
        radial_grad.setColorAt(0.0, glow_c1)
        radial_grad.setColorAt(0.6, glow_c2)
        radial_grad.setColorAt(1.0, QColor(8, 11, 18, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(radial_grad))
        painter.drawEllipse(QPointF(center_x, center_y), glow_radius, glow_radius)

        # Concentric thin orbit rings
        painter.setPen(ring_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(center_x, center_y), glow_radius * 0.85, glow_radius * 0.85)

        if self._state in ("speaking", "listening"):
            # Outer secondary pulse wave
            wave_radius = glow_radius * (0.95 + 0.15 * pulse)
            painter.setPen(QPen(glow_c1, 1.0))
            painter.drawEllipse(QPointF(center_x, center_y), wave_radius, wave_radius)

        # Geometric "A" Emblem
        top_vertex = QPointF(center_x, center_y - 36 * scale)
        bottom_left = QPointF(center_x - 30 * scale, center_y + 32 * scale)
        bottom_right = QPointF(center_x + 30 * scale, center_y + 32 * scale)

        a_path = QPainterPath()
        a_path.moveTo(top_vertex)
        a_path.lineTo(bottom_left)
        a_path.lineTo(bottom_right)
        a_path.closeSubpath()

        # Inner chevron cutout
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
        grad.setColorAt(0.0, QColor(accent_c))
        grad.setColorAt(1.0, QColor(ACCENT_PRIMARY if self._state != "muted" else TEXT_MUTED))

        painter.setPen(QPen(QColor(accent_c), 1.5))
        painter.setBrush(QBrush(grad))
        painter.drawPath(a_shape)

        # Crossbar
        cross_pen = QPen(QColor(234, 241, 255, int(180 + 75 * pulse) if self._state != "muted" else 60), 2.0)
        painter.setPen(cross_pen)
        painter.drawLine(
            QPointF(center_x - 22 * scale, center_y + 10 * scale),
            QPointF(center_x + 22 * scale, center_y + 10 * scale),
        )

        # Status text below emblem if in active state
        if status_text:
            painter.setPen(QPen(QColor(accent_c)))
            font = painter.font()
            font.setPointSize(int(8 * scale))
            font.setBold(True)
            painter.setFont(font)
            text_rect = QRectF(0, center_y + 40 * scale, self.width(), 20 * scale)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, status_text)
