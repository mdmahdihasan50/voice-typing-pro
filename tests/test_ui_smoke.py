import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from voice_typing_pro.main_window import MainWindow
from voice_typing_pro.settings import AppSettings, SettingsStore


def test_main_window_builds_with_bengali_defaults(tmp_path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    store = SettingsStore(tmp_path / "settings.json")
    store.save(AppSettings(floating_bar_visible=False))
    monkeypatch.setattr("voice_typing_pro.hotkeys.GlobalHotkeyManager.start", lambda self, settings: None)
    window = MainWindow(store, start_minimized=True)
    assert window.settings.dictation_language == "bn-BD"
    assert window.brand_label.text() == "বাংলা ভয়েস টাইপিং প্রো"
    assert window.editor.placeholderText()
    window._quitting = True
    window.tray.hide()
    window.floating_bar.hide()
    window.close()
    app.processEvents()


def test_toolbar_actions_select_all_and_show_feedback(tmp_path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    store = SettingsStore(tmp_path / "settings.json")
    store.save(AppSettings(floating_bar_visible=False))
    monkeypatch.setattr("voice_typing_pro.hotkeys.GlobalHotkeyManager.start", lambda self, settings: None)
    window = MainWindow(store, start_minimized=True)
    window.editor.setPlainText("বাংলা লেখা")

    window._select_all_with_feedback()
    assert window.editor.textCursor().selectedText() == "বাংলা লেখা"
    assert window.statusBar().currentMessage() == "সমস্ত লেখা নির্বাচন করা হয়েছে"

    window._copy_with_feedback()
    assert window.statusBar().currentMessage() == "ক্লিপবোর্ডে কপি হয়েছে"
    window._cut_with_feedback()
    assert window.editor.toPlainText() == ""
    assert window.statusBar().currentMessage() == "নির্বাচিত লেখা কাট করা হয়েছে"
    window._paste_with_feedback()
    assert window.editor.toPlainText() == "বাংলা লেখা"
    assert window.statusBar().currentMessage() == "লেখা পেস্ট করা হয়েছে"

    window._quitting = True
    window.tray.hide()
    window.floating_bar.hide()
    window.close()
    app.processEvents()
