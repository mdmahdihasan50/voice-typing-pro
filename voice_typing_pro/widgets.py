from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QWidget


def create_app_icon(size: int = 128) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#5B5FEF"))
    painter.drawRoundedRect(QRectF(4, 4, size - 8, size - 8), 28, 28)
    painter.setBrush(QColor("#FFFFFF"))
    mic = QRectF(size * 0.38, size * 0.20, size * 0.24, size * 0.42)
    painter.drawRoundedRect(mic, size * 0.12, size * 0.12)
    pen = QPen(QColor("#FFFFFF"), size * 0.055)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    path = QPainterPath()
    path.moveTo(size * 0.29, size * 0.48)
    path.cubicTo(size * 0.30, size * 0.75, size * 0.70, size * 0.75, size * 0.71, size * 0.48)
    painter.drawPath(path)
    painter.drawLine(QPointF(size * 0.5, size * 0.72), QPointF(size * 0.5, size * 0.84))
    painter.drawLine(QPointF(size * 0.38, size * 0.84), QPointF(size * 0.62, size * 0.84))
    painter.end()
    return QIcon(pixmap)


class WaveformWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(118, 44)
        self._phase = 0.0
        self._active = False
        self._processing = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(70)

    def set_state(self, state: str) -> None:
        self._active = state in {"listening", "calibrating", "processing", "loading_model"}
        self._processing = state in {"processing", "loading_model"}
        self.update()

    def _tick(self) -> None:
        if self._active:
            self._phase += 0.55 if self._processing else 0.35
            self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt API
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor("#F0A52B" if self._processing else "#5B5FEF")
        if not self._active:
            color = QColor("#8995A9")
        painter.setPen(QPen(color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        middle = self.height() / 2
        for index in range(9):
            x = 8 + index * 13
            if self._active:
                height = 8 + 22 * abs(math.sin(self._phase + index * 0.58))
            else:
                height = 5
            painter.drawLine(QPointF(x, middle - height / 2), QPointF(x, middle + height / 2))
