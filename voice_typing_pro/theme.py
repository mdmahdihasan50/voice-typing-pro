from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


LIGHT_QSS = """
QWidget { font-family: "Noto Sans Bengali", "Nirmala UI", "Segoe UI"; color: #172033; }
QMainWindow, QDialog { background: #F4F7FB; }
QFrame#Header, QFrame#StatusCard, QFrame#EditorCard { background: #FFFFFF; border: 1px solid #DFE6F0; border-radius: 16px; }
QLabel#Brand { color: #18243A; font-size: 22px; font-weight: 700; }
QLabel#Tagline, QLabel#Muted { color: #66738A; }
QLabel#StatusText { font-size: 15px; font-weight: 600; }
QPushButton { background: #EEF2F8; border: 1px solid #DCE4EF; border-radius: 9px; min-height: 34px; padding: 0 12px; }
QPushButton:hover { background: #E3EAF5; }
QPushButton:pressed { background: #D7E1EF; }
QPushButton#PrimaryButton { background: #5B5FEF; color: white; border: none; border-radius: 22px; min-height: 44px; font-weight: 700; padding: 0 22px; }
QPushButton#PrimaryButton:hover { background: #4B4FD8; }
QPushButton#DangerButton { background: #E94D67; color: white; border: none; }
QComboBox, QSpinBox, QLineEdit, QFontComboBox { background: #FFFFFF; border: 1px solid #CFD9E7; border-radius: 8px; min-height: 34px; padding: 0 9px; }
QComboBox::drop-down { border: none; width: 24px; }
QTextEdit { background: #FFFFFF; color: #172033; border: none; selection-background-color: #C8CBFF; padding: 14px; }
QToolBar { background: transparent; border: none; spacing: 4px; }
QToolButton { border-radius: 7px; padding: 6px 8px; }
QToolButton:hover { background: #E9EEF6; }
QMenuBar, QMenu { background: #FFFFFF; }
QMenu::item:selected { background: #E8E9FF; }
QStatusBar { background: #F4F7FB; color: #66738A; }
QCheckBox { spacing: 8px; }
QSlider::groove:horizontal { height: 4px; background: #D7DFEA; border-radius: 2px; }
QSlider::handle:horizontal { background: #5B5FEF; width: 14px; margin: -5px 0; border-radius: 7px; }
"""


DARK_QSS = """
QWidget { font-family: "Noto Sans Bengali", "Nirmala UI", "Segoe UI"; color: #E9EDF6; }
QMainWindow, QDialog { background: #11151D; }
QFrame#Header, QFrame#StatusCard, QFrame#EditorCard { background: #191F2A; border: 1px solid #2B3443; border-radius: 16px; }
QLabel#Brand { color: #F4F6FB; font-size: 22px; font-weight: 700; }
QLabel#Tagline, QLabel#Muted { color: #97A3B8; }
QLabel#StatusText { font-size: 15px; font-weight: 600; }
QPushButton { background: #252D3A; border: 1px solid #343E4E; border-radius: 9px; min-height: 34px; padding: 0 12px; }
QPushButton:hover { background: #303A49; }
QPushButton:pressed { background: #394557; }
QPushButton#PrimaryButton { background: #6C70F7; color: white; border: none; border-radius: 22px; min-height: 44px; font-weight: 700; padding: 0 22px; }
QPushButton#PrimaryButton:hover { background: #7D81FF; }
QPushButton#DangerButton { background: #E94D67; color: white; border: none; }
QComboBox, QSpinBox, QLineEdit, QFontComboBox { background: #202733; border: 1px solid #354052; border-radius: 8px; min-height: 34px; padding: 0 9px; }
QComboBox::drop-down { border: none; width: 24px; }
QTextEdit { background: #191F2A; color: #E9EDF6; border: none; selection-background-color: #5459B9; padding: 14px; }
QToolBar { background: transparent; border: none; spacing: 4px; }
QToolButton { border-radius: 7px; padding: 6px 8px; }
QToolButton:hover { background: #2A3341; }
QMenuBar, QMenu { background: #191F2A; }
QMenu::item:selected { background: #3C417F; }
QStatusBar { background: #11151D; color: #97A3B8; }
QCheckBox { spacing: 8px; }
QSlider::groove:horizontal { height: 4px; background: #3A4453; border-radius: 2px; }
QSlider::handle:horizontal { background: #7478FF; width: 14px; margin: -5px 0; border-radius: 7px; }
"""


def apply_theme(app: QApplication, theme: str) -> str:
    if theme == "system":
        color = app.palette().color(QPalette.ColorRole.Window)
        theme = "dark" if color.lightness() < 128 else "light"
    app.setStyleSheet(DARK_QSS if theme == "dark" else LIGHT_QSS)
    return theme
