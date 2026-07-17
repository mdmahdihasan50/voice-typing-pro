from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QByteArray, QSignalBlocker, QTimer, Qt
from PySide6.QtGui import QAction, QColor, QCloseEvent, QFont, QKeySequence, QPalette, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSlider,
    QStyle,
    QSystemTrayIcon,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .commands import CommandResult, process_recognition
from .dialogs import FindReplaceDialog, HelpDialog, SettingsDialog
from .exporters import export_docx, export_pdf
from .floating_bar import FloatingBar
from .history import HistoryStore
from .hotkeys import GlobalHotkeyManager
from .i18n import Translator
from .resources import register_bundled_fonts
from .settings import AppSettings, SettingsStore, update_settings
from .speech import SpeechEngine
from .startup import configure_windows_startup
from .theme import apply_theme
from .widgets import WaveformWidget, create_app_icon
from .windows_input import WindowsTextInjector


class MainWindow(QMainWindow):
    def __init__(
        self,
        settings_store: SettingsStore,
        *,
        start_minimized: bool = False,
    ) -> None:
        super().__init__()
        register_bundled_fonts()
        self.store = settings_store
        self.settings = self.store.load()
        self.tr = Translator(self.settings.ui_language)
        self.history = HistoryStore(self.store.history_path)
        self.speech = SpeechEngine()
        self.injector = WindowsTextInjector()
        self.hotkeys = GlobalHotkeyManager()
        self.current_file: Path | None = (
            Path(self.settings.last_file) if self.settings.last_file else None
        )
        self._current_state = "idle"
        self._listening = False
        self._quitting = False
        self._find_dialog: FindReplaceDialog | None = None
        self._last_startup_setting = self.settings.start_with_windows

        self.setWindowIcon(create_app_icon())
        self.setMinimumSize(820, 620)
        self.resize(1080, 760)
        self._build_ui()
        self._build_actions()
        self._build_tray()
        self._build_floating_bar()
        self._connect_services()
        self._restore_geometry()
        self.apply_settings(initial=True)
        self._restore_autosave()

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.start(2500)
        self.foreground_timer = QTimer(self)
        self.foreground_timer.timeout.connect(self.injector.observe_foreground_window)
        self.foreground_timer.start(300)

        should_minimize = start_minimized or self.settings.launch_minimized
        if not should_minimize:
            self.show()
        if self.settings.floating_bar_visible:
            self.show_floating_bar()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 16, 20, 12)
        root.setSpacing(12)
        self.setCentralWidget(central)

        self.header = QFrame()
        self.header.setObjectName("Header")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 14, 16, 14)
        brand_box = QVBoxLayout()
        self.brand_label = QLabel()
        self.brand_label.setObjectName("Brand")
        self.tagline_label = QLabel()
        self.tagline_label.setObjectName("Tagline")
        brand_box.addWidget(self.brand_label)
        brand_box.addWidget(self.tagline_label)
        header_layout.addLayout(brand_box, 1)
        self.language_button = QPushButton()
        self.language_button.clicked.connect(self.toggle_dictation_language)
        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumWidth(160)
        self.mode_combo.currentIndexChanged.connect(self._mode_changed)
        self.floating_button = QPushButton()
        self.floating_button.setCheckable(True)
        self.floating_button.clicked.connect(self._floating_toggled)
        self.help_button = QPushButton()
        self.help_button.clicked.connect(self.show_help)
        self.settings_button = QPushButton()
        self.settings_button.clicked.connect(self.open_settings)
        header_layout.addWidget(self.language_button)
        header_layout.addWidget(self.mode_combo)
        header_layout.addWidget(self.floating_button)
        header_layout.addWidget(self.help_button)
        header_layout.addWidget(self.settings_button)
        root.addWidget(self.header)

        self.status_card = QFrame()
        self.status_card.setObjectName("StatusCard")
        status_layout = QHBoxLayout(self.status_card)
        status_layout.setContentsMargins(20, 14, 20, 14)
        self.waveform = WaveformWidget()
        status_layout.addWidget(self.waveform)
        status_text_box = QVBoxLayout()
        self.status_label = QLabel()
        self.status_label.setObjectName("StatusText")
        self.hint_label = QLabel()
        self.hint_label.setObjectName("Muted")
        status_text_box.addWidget(self.status_label)
        status_text_box.addWidget(self.hint_label)
        status_layout.addLayout(status_text_box, 1)
        self.mic_button = QPushButton()
        self.mic_button.setObjectName("PrimaryButton")
        self.mic_button.clicked.connect(self.toggle_listening)
        status_layout.addWidget(self.mic_button)
        root.addWidget(self.status_card)

        self.editor_card = QFrame()
        self.editor_card.setObjectName("EditorCard")
        editor_layout = QVBoxLayout(self.editor_card)
        editor_layout.setContentsMargins(8, 7, 8, 8)
        editor_layout.setSpacing(0)
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        editor_layout.addWidget(self.toolbar)
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setUndoRedoEnabled(True)
        self.editor.textChanged.connect(self._update_counts)
        self.editor.cursorPositionChanged.connect(self._update_cursor_position)
        editor_layout.addWidget(self.editor, 1)
        footer = QHBoxLayout()
        footer.setContentsMargins(10, 3, 10, 4)
        self.count_label = QLabel()
        self.count_label.setObjectName("Muted")
        self.cursor_label = QLabel()
        self.cursor_label.setObjectName("Muted")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(11, 30)
        self.zoom_slider.setFixedWidth(120)
        self.zoom_slider.valueChanged.connect(self._font_size_changed)
        footer.addWidget(self.count_label)
        footer.addStretch(1)
        footer.addWidget(self.cursor_label)
        footer.addSpacing(10)
        footer.addWidget(QLabel("A−"))
        footer.addWidget(self.zoom_slider)
        footer.addWidget(QLabel("A+"))
        editor_layout.addLayout(footer)
        root.addWidget(self.editor_card, 1)
        self.statusBar().showMessage("")

    def _make_action(
        self,
        key: str,
        slot,
        shortcut: QKeySequence.StandardKey | str | None = None,
        icon=None,
    ) -> QAction:
        action = QAction(self.tr.t(key), self)
        action.setProperty("translation_key", key)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if icon is not None:
            action.setIcon(self.style().standardIcon(icon))
        action.triggered.connect(slot)
        return action

    def _build_actions(self) -> None:
        style = QStyle.StandardPixmap
        self.action_new = self._make_action("new", self.new_document, QKeySequence.StandardKey.New, style.SP_FileIcon)
        self.action_open = self._make_action("open", self.open_document, QKeySequence.StandardKey.Open, style.SP_DialogOpenButton)
        self.action_save = self._make_action("save", self.save_document, QKeySequence.StandardKey.Save, style.SP_DialogSaveButton)
        self.action_save_as = self._make_action("save_as", self.save_document_as, QKeySequence.StandardKey.SaveAs)
        self.action_docx = self._make_action("export_docx", self.export_to_docx)
        self.action_pdf = self._make_action("export_pdf", self.export_to_pdf)
        self.action_undo = self._make_action("undo", self.editor.undo, QKeySequence.StandardKey.Undo, style.SP_ArrowBack)
        self.action_redo = self._make_action("redo", self.editor.redo, QKeySequence.StandardKey.Redo, style.SP_ArrowForward)
        self.action_cut = self._make_action("cut", self._cut_with_feedback, QKeySequence.StandardKey.Cut)
        self.action_copy = self._make_action("copy", self._copy_with_feedback, QKeySequence.StandardKey.Copy)
        self.action_paste = self._make_action("paste", self._paste_with_feedback, QKeySequence.StandardKey.Paste)
        self.action_find = self._make_action("find", self.open_find, QKeySequence.StandardKey.Find)
        self.action_select_all = self._make_action("select_all", self._select_all_with_feedback, QKeySequence.StandardKey.SelectAll)
        self.action_clear = self._make_action("clear", self.clear_document)
        self.action_settings = self._make_action("settings", self.open_settings, "Ctrl+,")
        self.action_history = self._make_action("history", self.show_history)
        self.action_help = self._make_action("help_center", self.show_help, "F1")
        self.action_about = self._make_action("about", self.show_about)
        self.action_quit = self._make_action("quit", self.shutdown, "Ctrl+Q")

        for action in (
            self.action_new,
            self.action_open,
            self.action_save,
            self.action_undo,
            self.action_redo,
            self.action_cut,
            self.action_copy,
            self.action_select_all,
            self.action_paste,
            self.action_find,
        ):
            self.toolbar.addAction(action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_clear)

        self._rebuild_menus()

    def _rebuild_menus(self) -> None:
        self.menuBar().clear()
        file_menu = self.menuBar().addMenu(self.tr.t("file"))
        file_menu.addActions([self.action_new, self.action_open, self.action_save, self.action_save_as])
        recent_menu = file_menu.addMenu(self.tr.t("recent_files"))
        for file_name in self.settings.recent_files[:8]:
            action = recent_menu.addAction(Path(file_name).name)
            action.setToolTip(file_name)
            action.triggered.connect(
                lambda checked=False, path=file_name: self._open_recent_document(path)
            )
        recent_menu.setEnabled(bool(self.settings.recent_files))
        export_menu = file_menu.addMenu(self.tr.t("export"))
        export_menu.addActions([self.action_docx, self.action_pdf])
        file_menu.addSeparator()
        file_menu.addAction(self.action_quit)
        edit_menu = self.menuBar().addMenu(self.tr.t("edit"))
        edit_menu.addActions(
            [
                self.action_undo,
                self.action_redo,
                self.action_cut,
                self.action_copy,
                self.action_paste,
                self.action_find,
                self.action_select_all,
                self.action_clear,
            ]
        )
        tools_menu = self.menuBar().addMenu(self.tr.t("tools"))
        tools_menu.addActions([self.action_history, self.action_settings])
        help_menu = self.menuBar().addMenu(self.tr.t("help"))
        help_menu.addAction(self.action_help)
        help_menu.addAction(self.action_about)

    def _build_tray(self) -> None:
        self.tray = QSystemTrayIcon(create_app_icon(64), self)
        self.tray_menu = QMenu()
        self.tray_show_action = QAction(self.tr.t("show"), self)
        self.tray_toggle_action = QAction(self.tr.t("start"), self)
        self.tray_bn_action = QAction("বাংলা", self)
        self.tray_en_action = QAction("English", self)
        self.tray_float_action = QAction(self.tr.t("floating_bar"), self)
        self.tray_quit_action = QAction(self.tr.t("quit"), self)
        self.tray_show_action.triggered.connect(self.show_main_window)
        self.tray_toggle_action.triggered.connect(self.toggle_listening)
        self.tray_bn_action.triggered.connect(lambda: self.set_dictation_language("bn-BD"))
        self.tray_en_action.triggered.connect(lambda: self.set_dictation_language("en-US"))
        self.tray_float_action.triggered.connect(self.show_floating_bar)
        self.tray_quit_action.triggered.connect(self.shutdown)
        self.tray_menu.addAction(self.tray_show_action)
        self.tray_menu.addAction(self.tray_toggle_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.tray_bn_action)
        self.tray_menu.addAction(self.tray_en_action)
        self.tray_menu.addAction(self.tray_float_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.tray_quit_action)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _build_floating_bar(self) -> None:
        self.floating_bar = FloatingBar()
        self.floating_bar.toggle_listening.connect(self.toggle_listening)
        self.floating_bar.toggle_language.connect(self.toggle_dictation_language)
        self.floating_bar.toggle_mode.connect(self.toggle_mode)
        self.floating_bar.settings_requested.connect(self.open_settings)
        self.floating_bar.hidden.connect(self._floating_hidden)
        self.floating_bar.position_changed.connect(self._floating_moved)

    def _connect_services(self) -> None:
        self.speech.text_recognized.connect(self._on_text_recognized)
        self.speech.state_changed.connect(self._set_speech_state)
        self.speech.error_occurred.connect(self._on_speech_error)
        self.hotkeys.toggle_requested.connect(self.toggle_listening)
        self.hotkeys.bengali_requested.connect(lambda: self.set_dictation_language("bn-BD"))
        self.hotkeys.english_requested.connect(lambda: self.set_dictation_language("en-US"))
        self.hotkeys.push_started.connect(self._start_listening)
        self.hotkeys.push_stopped.connect(self._stop_listening)
        self.hotkeys.failed.connect(lambda detail: self.statusBar().showMessage(detail, 6000))

    def apply_settings(self, *, initial: bool = False) -> None:
        app = QApplication.instance()
        resolved_theme = "light"
        if app:
            resolved_theme = apply_theme(app, self.settings.theme)
        editor_palette = self.editor.palette()
        if resolved_theme == "dark":
            editor_palette.setColor(QPalette.ColorRole.Base, QColor("#191F2A"))
            editor_palette.setColor(QPalette.ColorRole.Text, QColor("#E9EDF6"))
            editor_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#8D99AD"))
        else:
            editor_palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            editor_palette.setColor(QPalette.ColorRole.Text, QColor("#172033"))
            editor_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#7D889A"))
        self.editor.setPalette(editor_palette)
        self.editor.viewport().setAutoFillBackground(True)
        self.tr.set_language(self.settings.ui_language)
        self.speech.configure(
            language=self.settings.dictation_language,
            device_index=self.settings.microphone_index,
            provider=self.settings.speech_engine,
            offline_model=self.settings.offline_model,
        )
        self.editor.setFont(QFont(self.settings.font_family, self.settings.font_size))
        with QSignalBlocker(self.zoom_slider):
            self.zoom_slider.setValue(self.settings.font_size)
        self.hotkeys.start(self.settings)
        self._set_always_on_top(self.settings.always_on_top)
        self._refresh_translations()
        self._sync_controls()
        if not initial and self.settings.start_with_windows != self._last_startup_setting:
            try:
                configure_windows_startup(self.settings.start_with_windows)
                self._last_startup_setting = self.settings.start_with_windows
            except OSError as exc:
                self.statusBar().showMessage(str(exc), 7000)
        self.store.save(self.settings)

    def _refresh_translations(self) -> None:
        self.setWindowTitle(self.tr.t("app_name"))
        self.brand_label.setText(self.tr.t("app_name"))
        self.tagline_label.setText(self.tr.t("tagline"))
        self.settings_button.setText(self.tr.t("settings"))
        self.help_button.setText(self.tr.t("help"))
        self.floating_button.setText(self.tr.t("floating_bar"))
        self.editor.setPlaceholderText(self.tr.t("placeholder"))
        with QSignalBlocker(self.mode_combo):
            self.mode_combo.clear()
            self.mode_combo.addItem(self.tr.t("internal"), "internal")
            self.mode_combo.addItem(self.tr.t("global"), "global")
            mode_index = self.mode_combo.findData(self.settings.typing_mode)
            self.mode_combo.setCurrentIndex(max(0, mode_index))
        for action in self.findChildren(QAction):
            key = action.property("translation_key")
            if key:
                action.setText(self.tr.t(key))
        self._rebuild_menus()
        self.tray_show_action.setText(self.tr.t("show"))
        self.tray_float_action.setText(self.tr.t("floating_bar"))
        self.tray_quit_action.setText(self.tr.t("quit"))
        self._set_speech_state(self._current_state)
        self._update_counts()
        self._update_cursor_position()

    def _sync_controls(self) -> None:
        self.language_button.setText(
            "বাংলা · BN" if self.settings.dictation_language == "bn-BD" else "English · EN"
        )
        self.floating_bar.set_language(self.settings.dictation_language)
        self.floating_bar.set_mode(self.settings.typing_mode)
        self.floating_bar.set_translations(self.tr.t("start"), self.tr.t("stop"))
        with QSignalBlocker(self.floating_button):
            self.floating_button.setChecked(self.settings.floating_bar_visible)
        with QSignalBlocker(self.mode_combo):
            index = self.mode_combo.findData(self.settings.typing_mode)
            self.mode_combo.setCurrentIndex(max(index, 0))
        self.hint_label.setText(
            self.tr.t("global_hint")
            if self.settings.typing_mode == "global"
            else self.tr.t("internal_hint")
        )

    def toggle_listening(self) -> None:
        if self._listening:
            self._stop_listening()
        else:
            self._start_listening()

    def _start_listening(self) -> None:
        if self._listening:
            return
        if self.settings.typing_mode == "global":
            self.injector.observe_foreground_window()
        self._listening = True
        self.speech.start()
        self._set_speech_state("calibrating")

    def _stop_listening(self) -> None:
        if not self._listening:
            return
        self.speech.stop()
        self._listening = False
        self._set_speech_state("stopped")

    def _set_speech_state(self, state: str) -> None:
        self._current_state = state
        if state == "error":
            self._listening = False
        self.status_label.setText(self.tr.t(state if state in {
            "idle", "calibrating", "listening", "processing", "loading_model", "stopped", "error"
        } else "ready"))
        self.waveform.set_state(state)
        self.mic_button.setText(self.tr.t("stop") if self._listening else self.tr.t("start"))
        self.tray_toggle_action.setText(self.tr.t("stop") if self._listening else self.tr.t("start"))
        self.floating_bar.set_state(state, self._listening)

    def _on_speech_error(self, key: str, detail: str) -> None:
        message = self.tr.t(key if key in {"no_microphone", "network_error", "not_understood", "error"} else "error")
        self.statusBar().showMessage(f"{message}: {detail}" if detail else message, 7000)

    def _on_text_recognized(self, raw_text: str) -> None:
        result = process_recognition(
            raw_text,
            self.settings.dictation_language,
            commands_enabled=self.settings.voice_commands,
            punctuation_enabled=self.settings.automatic_punctuation,
            bengali_digits=self.settings.bengali_digits,
        )
        if result.action:
            self._execute_voice_action(result.action)
            return
        if not result.text:
            return
        if self.settings.typing_mode == "internal":
            self._insert_editor_text(result.text)
        else:
            self.injector.inject(result.text + " ")
        self.history.add(result.text, self.settings.dictation_language)

    def _execute_voice_action(self, action: str) -> None:
        if action == "language_bn":
            self.set_dictation_language("bn-BD")
        elif action == "language_en":
            self.set_dictation_language("en-US")
        elif action == "stop":
            self.toggle_listening()
        elif action in {"undo_word", "undo_sentence"}:
            if self.settings.typing_mode == "global":
                self.injector.undo()
            else:
                self._delete_previous_unit(sentence=action == "undo_sentence")
        elif action == "clear" and self.settings.typing_mode == "internal":
            self.clear_document()
        elif action in {"newline", "paragraph"}:
            value = "\n\n" if action == "paragraph" else "\n"
            if self.settings.typing_mode == "internal":
                self.editor.textCursor().insertText(value)
            else:
                self.injector.press_enter(2 if action == "paragraph" else 1)

    def _insert_editor_text(self, text: str) -> None:
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        document_text = self.editor.toPlainText()
        position = cursor.position()
        previous = document_text[position - 1] if position > 0 else ""
        prefix = "" if not previous or previous.isspace() or text[:1] in ",.;:!?।" else " "
        cursor.insertText(prefix + text + ("" if text.endswith("\n") else " "))
        cursor.endEditBlock()
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()

    def _delete_previous_unit(self, *, sentence: bool) -> None:
        cursor = self.editor.textCursor()
        if sentence:
            text = self.editor.toPlainText()[: cursor.position()].rstrip()
            boundary = max(text.rfind(mark) for mark in ("।", ".", "?", "!", "\n"))
            cursor.setPosition(boundary + 1 if boundary >= 0 else 0, QTextCursor.MoveMode.KeepAnchor)
        else:
            cursor.movePosition(QTextCursor.MoveOperation.PreviousWord, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()

    def set_dictation_language(self, language: str) -> None:
        self.settings.dictation_language = language if language in {"bn-BD", "en-US"} else "bn-BD"
        self.speech.configure(
            language=self.settings.dictation_language,
            device_index=self.settings.microphone_index,
            provider=self.settings.speech_engine,
            offline_model=self.settings.offline_model,
        )
        self._sync_controls()
        self.store.save(self.settings)

    def toggle_dictation_language(self) -> None:
        self.set_dictation_language(
            "en-US" if self.settings.dictation_language == "bn-BD" else "bn-BD"
        )

    def _mode_changed(self) -> None:
        mode = self.mode_combo.currentData()
        if mode in {"internal", "global"}:
            self.settings.typing_mode = mode
            self._sync_controls()
            self.store.save(self.settings)

    def toggle_mode(self) -> None:
        self.settings.typing_mode = "global" if self.settings.typing_mode == "internal" else "internal"
        self._sync_controls()
        self.store.save(self.settings)

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self.tr, self.speech.input_devices(), self)
        if dialog.exec():
            update_settings(self.settings, dialog.values())
            self.apply_settings()
            if self.settings.floating_bar_visible:
                self.show_floating_bar()

    def new_document(self) -> None:
        if not self._confirm_discard():
            return
        self.editor.clear()
        self.editor.document().setModified(False)
        self.current_file = None
        self.settings.last_file = ""
        self._clear_autosave()
        self._update_title()

    def open_document(self) -> None:
        if not self._confirm_discard():
            return
        name, _ = QFileDialog.getOpenFileName(
            self, self.tr.t("open"), "", "Text files (*.txt *.md);;All files (*.*)"
        )
        if not name:
            return
        self._open_document_path(Path(name))

    def _open_recent_document(self, name: str) -> None:
        if not self._confirm_discard():
            return
        self._open_document_path(Path(name))

    def _open_document_path(self, path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            QMessageBox.critical(self, self.tr.t("error"), str(exc))
            self.settings.recent_files = [item for item in self.settings.recent_files if item != str(path)]
            self.store.save(self.settings)
            return
        self.editor.setPlainText(text)
        self.editor.document().setModified(False)
        self.current_file = path
        self.settings.last_file = str(path)
        self._remember_recent(path)
        self._clear_autosave()
        self._update_title()
        self.statusBar().showMessage(self.tr.t("opened"), 3500)

    def save_document(self) -> bool:
        if self.current_file is None:
            return self.save_document_as()
        return self._write_document(self.current_file)

    def save_document_as(self) -> bool:
        name, _ = QFileDialog.getSaveFileName(
            self, self.tr.t("save_as"), "", "Text files (*.txt);;Markdown (*.md);;All files (*.*)"
        )
        if not name:
            return False
        self.current_file = Path(name)
        self.settings.last_file = name
        return self._write_document(self.current_file)

    def _write_document(self, path: Path) -> bool:
        try:
            path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, self.tr.t("error"), str(exc))
            return False
        self.editor.document().setModified(False)
        self._remember_recent(path)
        self.store.save(self.settings)
        self._clear_autosave()
        self._update_title()
        self.statusBar().showMessage(self.tr.t("saved"), 3500)
        return True

    def export_to_docx(self) -> None:
        name, _ = QFileDialog.getSaveFileName(self, self.tr.t("export_docx"), "", "Word (*.docx)")
        if not name:
            return
        if not name.lower().endswith(".docx"):
            name += ".docx"
        try:
            export_docx(self.editor.toPlainText(), name, self.settings.font_family, self.settings.font_size)
            self.statusBar().showMessage(self.tr.t("exported"), 3500)
        except Exception as exc:
            QMessageBox.critical(self, self.tr.t("error"), str(exc))

    def export_to_pdf(self) -> None:
        name, _ = QFileDialog.getSaveFileName(self, self.tr.t("export_pdf"), "", "PDF (*.pdf)")
        if not name:
            return
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        try:
            export_pdf(self.editor.toPlainText(), name, self.settings.font_family, self.settings.font_size)
            self.statusBar().showMessage(self.tr.t("exported"), 3500)
        except Exception as exc:
            QMessageBox.critical(self, self.tr.t("error"), str(exc))

    def clear_document(self) -> None:
        if not self.editor.toPlainText():
            return
        answer = QMessageBox.question(self, self.tr.t("clear"), self.tr.t("confirm_clear"))
        if answer == QMessageBox.StandardButton.Yes:
            self.editor.clear()
            self._show_feedback("clear_done")

    def open_find(self) -> None:
        if self._find_dialog is None:
            self._find_dialog = FindReplaceDialog(self.editor, self.tr, self)
        self._find_dialog.show()
        self._find_dialog.raise_()
        self._find_dialog.activateWindow()
        self._show_feedback("find_opened")

    def _cut_with_feedback(self) -> None:
        if not self.editor.textCursor().hasSelection():
            self._show_feedback("select_text_first")
            return
        self.editor.cut()
        self._show_feedback("cut_done")

    def _copy_with_feedback(self) -> None:
        if not self.editor.textCursor().hasSelection():
            self._show_feedback("select_text_first")
            return
        self.editor.copy()
        self._show_feedback("copied")

    def _paste_with_feedback(self) -> None:
        if not self.editor.canPaste():
            self._show_feedback("clipboard_empty")
            return
        self.editor.paste()
        self._show_feedback("paste_done")

    def _select_all_with_feedback(self) -> None:
        if not self.editor.toPlainText():
            self._show_feedback("nothing_to_select")
            return
        self.editor.selectAll()
        self.editor.setFocus()
        self._show_feedback("select_all_done")

    def _show_feedback(self, translation_key: str) -> None:
        self.statusBar().showMessage(self.tr.t(translation_key), 3500)

    def show_history(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr.t("history"))
        dialog.resize(620, 420)
        layout = QVBoxLayout(dialog)
        history_list = QListWidget()
        for entry in self.history.load():
            text = entry.get("text", "")
            if text:
                history_list.addItem(text)
        layout.addWidget(history_list, 1)
        buttons = QHBoxLayout()
        insert_button = QPushButton(self.tr.t("insert"))
        clear_button = QPushButton(self.tr.t("clear_history"))
        close_button = QPushButton(self.tr.t("close"))
        buttons.addWidget(insert_button)
        buttons.addWidget(clear_button)
        buttons.addStretch(1)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

        def insert_selected() -> None:
            if item := history_list.currentItem():
                self._insert_editor_text(item.text())
                dialog.accept()

        insert_button.clicked.connect(insert_selected)
        history_list.itemDoubleClicked.connect(lambda item: insert_selected())
        clear_button.clicked.connect(lambda: (self.history.clear(), history_list.clear()))
        close_button.clicked.connect(dialog.reject)
        dialog.exec()

    def _remember_recent(self, path: Path) -> None:
        value = str(path.resolve())
        self.settings.recent_files = [
            value, *[item for item in self.settings.recent_files if item != value]
        ][:8]
        self._rebuild_menus()

    def show_about(self) -> None:
        HelpDialog(self.tr, self, start_tab=1).exec()

    def show_help(self) -> None:
        HelpDialog(self.tr, self).exec()

    def _update_counts(self) -> None:
        text = self.editor.toPlainText()
        self.count_label.setText(self.tr.t("words_chars", words=len(text.split()), chars=len(text)))
        self._update_title()

    def _update_cursor_position(self) -> None:
        cursor = self.editor.textCursor()
        self.cursor_label.setText(
            self.tr.t("line_column", line=cursor.blockNumber() + 1, column=cursor.positionInBlock() + 1)
        )

    def _font_size_changed(self, value: int) -> None:
        self.settings.font_size = value
        self.editor.setFont(QFont(self.settings.font_family, value))

    def _update_title(self) -> None:
        filename = self.current_file.name if self.current_file else self.tr.t("new")
        marker = " •" if self.editor.document().isModified() else ""
        self.setWindowTitle(f"{filename}{marker} — {self.tr.t('app_name')}")

    def _autosave(self) -> None:
        if not self.settings.auto_save or not self.editor.document().isModified():
            return
        try:
            self.store.autosave_path.parent.mkdir(parents=True, exist_ok=True)
            self.store.autosave_path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError:
            pass

    def _restore_autosave(self) -> None:
        path = self.store.autosave_path
        if not self.settings.auto_save or not path.exists():
            return
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return
        if text:
            self.editor.setPlainText(text)
            self.editor.document().setModified(True)
            self.statusBar().showMessage(self.tr.t("autosave_restored"), 6000)

    def _clear_autosave(self) -> None:
        try:
            self.store.autosave_path.unlink(missing_ok=True)
        except OSError:
            pass

    def _confirm_discard(self) -> bool:
        if not self.editor.document().isModified():
            return True
        answer = QMessageBox.question(
            self,
            self.tr.t("app_name"),
            self.tr.t("confirm_new"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def show_floating_bar(self) -> None:
        if self.settings.floating_x is not None and self.settings.floating_y is not None:
            self.floating_bar.move(self.settings.floating_x, self.settings.floating_y)
        elif screen := QApplication.primaryScreen():
            area = screen.availableGeometry()
            self.floating_bar.adjustSize()
            self.floating_bar.move(area.center().x() - self.floating_bar.width() // 2, area.top() + 12)
        self.floating_bar.show()
        self.settings.floating_bar_visible = True
        self._sync_controls()
        self.store.save(self.settings)

    def _floating_toggled(self, checked: bool) -> None:
        if checked:
            self.show_floating_bar()
        else:
            self.floating_bar.hide()
            self._floating_hidden()

    def _floating_hidden(self) -> None:
        self.settings.floating_bar_visible = False
        self._sync_controls()
        self.store.save(self.settings)

    def _floating_moved(self, x: int, y: int) -> None:
        self.settings.floating_x = x
        self.settings.floating_y = y
        self.store.save(self.settings)

    def _set_always_on_top(self, enabled: bool) -> None:
        was_visible = self.isVisible()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, enabled)
        if was_visible:
            self.show()

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()

    def show_main_window(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _restore_geometry(self) -> None:
        if not self.settings.window_geometry:
            return
        try:
            data = QByteArray.fromBase64(self.settings.window_geometry.encode("ascii"))
            self.restoreGeometry(data)
        except Exception:
            pass

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - Qt API
        if not self._quitting and self.tray.isVisible():
            event.ignore()
            self.hide()
            return
        if self.editor.document().isModified():
            self._autosave()
        event.accept()

    def shutdown(self) -> None:
        self._quitting = True
        self.settings.window_geometry = bytes(self.saveGeometry().toBase64()).decode("ascii")
        self.settings.font_size = self.zoom_slider.value()
        self.store.save(self.settings)
        self.speech.shutdown()
        self.hotkeys.stop()
        self.floating_bar.close()
        self.tray.hide()
        self.close()
        QApplication.quit()
