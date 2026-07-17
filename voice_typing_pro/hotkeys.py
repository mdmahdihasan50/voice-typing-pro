from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from pynput import keyboard

from .settings import AppSettings


class GlobalHotkeyManager(QObject):
    toggle_requested = Signal()
    bengali_requested = Signal()
    english_requested = Signal()
    push_started = Signal()
    push_stopped = Signal()
    failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._listener: keyboard.GlobalHotKeys | None = None
        self._push_listener: keyboard.Listener | None = None
        self._push_down = False

    def start(self, settings: AppSettings) -> None:
        self.stop()
        try:
            self._listener = keyboard.GlobalHotKeys(
                {
                    settings.hotkey_toggle: self.toggle_requested.emit,
                    settings.hotkey_bengali: self.bengali_requested.emit,
                    settings.hotkey_english: self.english_requested.emit,
                }
            )
            self._listener.start()
            if settings.listening_mode == "push_to_talk":
                self._push_listener = keyboard.Listener(
                    on_press=self._on_push_press,
                    on_release=self._on_push_release,
                )
                self._push_listener.start()
        except Exception as exc:  # pynput exposes platform-specific errors
            self._listener = None
            self.failed.emit(str(exc))

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        if self._push_listener is not None:
            self._push_listener.stop()
            self._push_listener = None
        self._push_down = False

    def _on_push_press(self, key) -> None:
        if key == keyboard.Key.f9 and not self._push_down:
            self._push_down = True
            self.push_started.emit()

    def _on_push_release(self, key) -> None:
        if key == keyboard.Key.f9 and self._push_down:
            self._push_down = False
            self.push_stopped.emit()
