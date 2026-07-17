from __future__ import annotations

import logging
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication, QMessageBox

from . import APP_DISPLAY_NAME, __version__
from .main_window import MainWindow
from .settings import SettingsStore
from .widgets import create_app_icon


def _configure_logging(store: SettingsStore) -> None:
    store.data_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=store.data_dir / "voice-typing-pro.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )


def run() -> int:
    application = QApplication(sys.argv)
    application.setApplicationName(APP_DISPLAY_NAME)
    application.setApplicationVersion(__version__)
    application.setOrganizationName("Mahdi Hasan")
    application.setQuitOnLastWindowClosed(False)
    application.setWindowIcon(create_app_icon())

    lock = QLockFile(str(Path(tempfile.gettempdir()) / "voice-typing-pro-v2.lock"))
    lock.setStaleLockTime(5000)
    if not lock.tryLock(100):
        QMessageBox.information(
            None,
            APP_DISPLAY_NAME,
            "বাংলা ভয়েস টাইপিং প্রো ইতিমধ্যে চলছে। System tray পরীক্ষা করুন।",
        )
        return 0

    store = SettingsStore()
    _configure_logging(store)

    def report_exception(exc_type, exc_value, traceback) -> None:
        logging.exception("Unhandled application error", exc_info=(exc_type, exc_value, traceback))
        QMessageBox.critical(None, APP_DISPLAY_NAME, str(exc_value))

    sys.excepthook = report_exception
    start_minimized = "--minimized" in sys.argv
    window = MainWindow(store, start_minimized=start_minimized)
    application._main_window = window  # keep Python ownership for the app lifetime
    application._instance_lock = lock
    return application.exec()
