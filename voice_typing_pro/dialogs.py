from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFontComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .i18n import Translator
from .help_content import developer_html, guide_html
from .settings import AppSettings


class FindReplaceDialog(QDialog):
    def __init__(self, editor: QTextEdit, translator: Translator, parent=None) -> None:
        super().__init__(parent)
        self.editor = editor
        self.tr = translator
        self.setModal(False)
        self.setMinimumWidth(420)
        layout = QFormLayout(self)
        self.find_edit = QLineEdit()
        self.replace_edit = QLineEdit()
        layout.addRow(self.tr.t("find_label"), self.find_edit)
        layout.addRow(self.tr.t("replace_label"), self.replace_edit)
        buttons = QHBoxLayout()
        find_button = QPushButton(self.tr.t("find_next"))
        replace_button = QPushButton(self.tr.t("replace_one"))
        all_button = QPushButton(self.tr.t("replace_all"))
        buttons.addWidget(find_button)
        buttons.addWidget(replace_button)
        buttons.addWidget(all_button)
        layout.addRow(buttons)
        find_button.clicked.connect(self.find_next)
        replace_button.clicked.connect(self.replace_one)
        all_button.clicked.connect(self.replace_all)
        self.find_edit.returnPressed.connect(self.find_next)

    def find_next(self) -> None:
        needle = self.find_edit.text()
        if not needle:
            return
        if not self.editor.find(needle):
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            if not self.editor.find(needle):
                QMessageBox.information(self, self.tr.t("find"), self.tr.t("no_match"))

    def replace_one(self) -> None:
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.find_edit.text():
            cursor.insertText(self.replace_edit.text())
        self.find_next()

    def replace_all(self) -> None:
        needle = self.find_edit.text()
        if not needle:
            return
        text = self.editor.toPlainText()
        replaced = text.replace(needle, self.replace_edit.text())
        if replaced == text:
            QMessageBox.information(self, self.tr.t("replace"), self.tr.t("no_match"))
            return
        cursor = self.editor.textCursor()
        position = cursor.position()
        self.editor.setPlainText(replaced)
        cursor = self.editor.textCursor()
        cursor.setPosition(min(position, len(replaced)))
        self.editor.setTextCursor(cursor)


class SettingsDialog(QDialog):
    def __init__(
        self,
        settings: AppSettings,
        translator: Translator,
        microphones: list[tuple[int, str]],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self.tr = translator
        self.setWindowTitle(self.tr.t("settings"))
        self.setMinimumWidth(560)
        root = QVBoxLayout(self)
        tabs = QTabWidget()
        root.addWidget(tabs)

        general = QWidget()
        form = QFormLayout(general)
        self.ui_language = QComboBox()
        self.ui_language.addItem("বাংলা", "bn")
        self.ui_language.addItem("English", "en")
        self._select_data(self.ui_language, settings.ui_language)
        form.addRow(self.tr.t("ui_language"), self.ui_language)

        self.voice_language = QComboBox()
        self.voice_language.addItem("বাংলা (বাংলাদেশ)", "bn-BD")
        self.voice_language.addItem("English (United States)", "en-US")
        self._select_data(self.voice_language, settings.dictation_language)
        form.addRow(self.tr.t("voice_language"), self.voice_language)

        self.theme = QComboBox()
        for key, value in (
            ("theme_system", "system"),
            ("theme_light", "light"),
            ("theme_dark", "dark"),
        ):
            self.theme.addItem(self.tr.t(key), value)
        self._select_data(self.theme, settings.theme)
        form.addRow(self.tr.t("theme"), self.theme)

        self.font = QFontComboBox()
        self.font.setCurrentFont(self.font.currentFont())
        index = self.font.findText(settings.font_family)
        if index >= 0:
            self.font.setCurrentIndex(index)
        form.addRow(self.tr.t("font"), self.font)
        self.font_size = QSpinBox()
        self.font_size.setRange(11, 36)
        self.font_size.setValue(settings.font_size)
        form.addRow(self.tr.t("font_size"), self.font_size)

        self.autosave = QCheckBox(self.tr.t("autosave"))
        self.autosave.setChecked(settings.auto_save)
        self.startup = QCheckBox(self.tr.t("startup"))
        self.startup.setChecked(settings.start_with_windows)
        self.minimized = QCheckBox(self.tr.t("launch_minimized"))
        self.minimized.setChecked(settings.launch_minimized)
        self.always_on_top = QCheckBox(self.tr.t("always_on_top"))
        self.always_on_top.setChecked(settings.always_on_top)
        form.addRow(self.autosave)
        form.addRow(self.always_on_top)
        form.addRow(self.startup)
        form.addRow(self.minimized)
        tabs.addTab(general, self.tr.t("settings"))

        speech = QWidget()
        speech_form = QFormLayout(speech)
        self.engine = QComboBox()
        self.engine.addItem(self.tr.t("google_online"), "google")
        self.engine.addItem(self.tr.t("whisper_offline"), "whisper")
        self._select_data(self.engine, settings.speech_engine)
        speech_form.addRow(self.tr.t("speech_engine"), self.engine)
        self.listening_mode = QComboBox()
        self.listening_mode.addItem(self.tr.t("continuous_mode"), "continuous")
        self.listening_mode.addItem(self.tr.t("push_to_talk"), "push_to_talk")
        self._select_data(self.listening_mode, settings.listening_mode)
        speech_form.addRow(self.tr.t("listening_mode"), self.listening_mode)
        self.model = QComboBox()
        for key, value in (
            ("model_tiny", "tiny"),
            ("model_base", "base"),
            ("model_small", "small"),
        ):
            self.model.addItem(self.tr.t(key), value)
        self._select_data(self.model, settings.offline_model)
        speech_form.addRow(self.tr.t("offline_model"), self.model)
        note = QLabel(self.tr.t("offline_download_note"))
        note.setWordWrap(True)
        note.setObjectName("Muted")
        speech_form.addRow(note)
        self.microphone = QComboBox()
        self.microphone.addItem(self.tr.t("default_microphone"), None)
        for index, name in microphones:
            self.microphone.addItem(f"{index}: {name}", index)
        self._select_data(self.microphone, settings.microphone_index)
        speech_form.addRow(self.tr.t("microphone"), self.microphone)
        self.commands = QCheckBox(self.tr.t("voice_commands"))
        self.commands.setChecked(settings.voice_commands)
        self.punctuation = QCheckBox(self.tr.t("punctuation"))
        self.punctuation.setChecked(settings.automatic_punctuation)
        self.digits = QCheckBox(self.tr.t("bengali_digits"))
        self.digits.setChecked(settings.bengali_digits)
        speech_form.addRow(self.commands)
        speech_form.addRow(self.punctuation)
        speech_form.addRow(self.digits)
        tabs.addTab(speech, self.tr.t("microphone"))

        hint = QLabel(self.tr.t("hotkey_hint"))
        hint.setObjectName("Muted")
        hint.setWordWrap(True)
        root.addWidget(hint)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Apply
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(self.tr.t("cancel"))
        buttons.button(QDialogButtonBox.StandardButton.Apply).setText(self.tr.t("apply"))
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.accept)
        root.addWidget(buttons)

    @staticmethod
    def _select_data(combo: QComboBox, value) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def values(self) -> dict[str, object]:
        return {
            "ui_language": self.ui_language.currentData(),
            "dictation_language": self.voice_language.currentData(),
            "theme": self.theme.currentData(),
            "font_family": self.font.currentFont().family(),
            "font_size": self.font_size.value(),
            "auto_save": self.autosave.isChecked(),
            "start_with_windows": self.startup.isChecked(),
            "launch_minimized": self.minimized.isChecked(),
            "always_on_top": self.always_on_top.isChecked(),
            "speech_engine": self.engine.currentData(),
            "listening_mode": self.listening_mode.currentData(),
            "offline_model": self.model.currentData(),
            "microphone_index": self.microphone.currentData(),
            "voice_commands": self.commands.isChecked(),
            "automatic_punctuation": self.punctuation.isChecked(),
            "bengali_digits": self.digits.isChecked(),
        }


class HelpDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        parent=None,
        *,
        start_tab: int = 0,
    ) -> None:
        super().__init__(parent)
        self.tr = translator
        self.setWindowTitle(self.tr.t("help_center"))
        self.resize(780, 680)
        self.setMinimumSize(620, 520)
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        guide = QTextBrowser()
        guide.setOpenExternalLinks(True)
        guide.setHtml(guide_html(self.tr.language))
        tabs.addTab(guide, self.tr.t("user_guide"))

        developer = QTextBrowser()
        developer.setOpenExternalLinks(True)
        developer.setHtml(developer_html(self.tr.language))
        tabs.addTab(developer, self.tr.t("developer_profile"))
        tabs.setCurrentIndex(1 if start_tab == 1 else 0)
        layout.addWidget(tabs, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(self.tr.t("close"))
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
