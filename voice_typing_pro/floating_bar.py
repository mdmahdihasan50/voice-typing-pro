from __future__ import annotations

import ctypes
import sys

from PySide6.QtCore import QPoint, Signal, Qt, QTimer
from PySide6.QtGui import QCloseEvent, QMouseEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget


class FloatingBar(QWidget):
    toggle_listening = Signal()
    toggle_language = Signal()
    toggle_mode = Signal()
    settings_requested = Signal()
    hidden = Signal()
    position_changed = Signal(int, int)

    def __init__(self) -> None:
        super().__init__(None)
        self.setObjectName("FloatingBar")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedHeight(58)
        self.setMinimumWidth(410)
        self._drag_origin: QPoint | None = None
        self._state = "idle"
        self._listening = False
        self._start_text = "শুরু"
        self._stop_text = "থামুন"

        panel = QFrame(self)
        panel.setObjectName("FloatingPanel")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 7, 8, 7)
        layout.setSpacing(7)
        self.language_button = QPushButton("বাংলা · BN")
        self.language_button.setObjectName("LanguagePill")
        self.language_button.clicked.connect(self.toggle_language)
        self.state_dot = QLabel("●")
        self.state_dot.setObjectName("StateDot")
        self.mic_button = QPushButton("●  শুরু")
        self.mic_button.setObjectName("FloatingMic")
        self.mic_button.clicked.connect(self.toggle_listening)
        self.mode_button = QPushButton("PAD")
        self.mode_button.setObjectName("ModePill")
        self.mode_button.clicked.connect(self.toggle_mode)
        settings_button = QPushButton("⋮")
        settings_button.setFixedWidth(38)
        settings_button.clicked.connect(self.settings_requested)
        hide_button = QPushButton("—")
        hide_button.setFixedWidth(34)
        hide_button.clicked.connect(self._hide_bar)
        layout.addWidget(self.language_button)
        layout.addWidget(self.state_dot)
        layout.addWidget(self.mic_button, 1)
        layout.addWidget(self.mode_button)
        layout.addWidget(settings_button)
        layout.addWidget(hide_button)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.addWidget(panel)
        self._apply_style()

    def _apply_style(self) -> None:
        active = self._state in {"listening", "calibrating"}
        processing = self._state in {"processing", "loading_model"}
        color = "#F2A93B" if processing else ("#46D39A" if active else "#8390A4")
        self.setStyleSheet(
            f"""
            QFrame#FloatingPanel {{ background: #171D27; border: 1px solid #303A49; border-radius: 17px; }}
            QPushButton {{ color: #EEF2FA; background: #252E3C; border: 1px solid #364253; border-radius: 9px; min-height: 34px; padding: 0 10px; }}
            QPushButton:hover {{ background: #323D4E; }}
            QPushButton#FloatingMic {{ background: #5B5FEF; border: none; font-weight: 700; min-width: 105px; }}
            QPushButton#LanguagePill {{ min-width: 88px; }}
            QPushButton#ModePill {{ min-width: 52px; font-weight: 700; }}
            QLabel#StateDot {{ color: {color}; font-size: 18px; }}
            """
        )

    def set_state(self, state: str, listening: bool) -> None:
        self._state = state
        self._listening = listening
        self.mic_button.setText(
            f"■  {self._stop_text}" if listening else f"●  {self._start_text}"
        )
        self._apply_style()

    def set_translations(self, start_text: str, stop_text: str) -> None:
        self._start_text = start_text
        self._stop_text = stop_text
        self.set_state(self._state, self._listening)

    def set_language(self, language: str) -> None:
        self.language_button.setText("বাংলা · BN" if language.startswith("bn") else "English · EN")

    def set_mode(self, mode: str) -> None:
        self.mode_button.setText("PAD" if mode == "internal" else "GLOBAL")

    def showEvent(self, event) -> None:  # noqa: N802 - Qt API
        super().showEvent(event)
        QTimer.singleShot(0, self._make_no_activate)

    def _make_no_activate(self) -> None:
        if sys.platform != "win32":
            return
        hwnd = int(self.winId())
        user32 = ctypes.windll.user32
        gwl_exstyle = -20
        ws_ex_noactivate = 0x08000000
        ws_ex_toolwindow = 0x00000080
        style = user32.GetWindowLongW(hwnd, gwl_exstyle)
        user32.SetWindowLongW(
            hwnd, gwl_exstyle, style | ws_ex_noactivate | ws_ex_toolwindow
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_origin)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._drag_origin = None
        self.position_changed.emit(self.x(), self.y())
        super().mouseReleaseEvent(event)

    def _hide_bar(self) -> None:
        self.hide()
        self.hidden.emit()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        event.ignore()
        self._hide_bar()
