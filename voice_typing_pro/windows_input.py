from __future__ import annotations

import ctypes
import os
import sys
import time
from ctypes import wintypes


IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    ULONG_PTR = wintypes.WPARAM

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = (
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        )

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = (
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        )

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = (
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD),
        )

    class _INPUTUNION(ctypes.Union):
        _fields_ = (("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT))

    class INPUT(ctypes.Structure):
        _anonymous_ = ("union",)
        _fields_ = (("type", wintypes.DWORD), ("union", _INPUTUNION))


class WindowsTextInjector:
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004
    INPUT_KEYBOARD = 1

    def __init__(self) -> None:
        self.target_hwnd: int | None = None
        self._user32 = ctypes.windll.user32 if IS_WINDOWS else None

    def observe_foreground_window(self) -> None:
        if not self._user32:
            return
        hwnd = int(self._user32.GetForegroundWindow())
        if not hwnd:
            return
        process_id = wintypes.DWORD()
        self._user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        if process_id.value != os.getpid():
            self.target_hwnd = hwnd

    def inject(self, text: str, *, restore_target: bool = True) -> bool:
        if not text:
            return True
        if not self._user32:
            return False
        if restore_target and self.target_hwnd:
            current = int(self._user32.GetForegroundWindow())
            if current != self.target_hwnd:
                self._user32.SetForegroundWindow(self.target_hwnd)
                time.sleep(0.04)

        encoded = text.encode("utf-16-le")
        units = [
            int.from_bytes(encoded[index : index + 2], "little")
            for index in range(0, len(encoded), 2)
        ]
        events: list[INPUT] = []
        for unit in units:
            events.append(
                INPUT(
                    type=self.INPUT_KEYBOARD,
                    ki=KEYBDINPUT(0, unit, self.KEYEVENTF_UNICODE, 0, 0),
                )
            )
            events.append(
                INPUT(
                    type=self.INPUT_KEYBOARD,
                    ki=KEYBDINPUT(
                        0,
                        unit,
                        self.KEYEVENTF_UNICODE | self.KEYEVENTF_KEYUP,
                        0,
                        0,
                    ),
                )
            )
        if not events:
            return True
        array_type = INPUT * len(events)
        sent = self._user32.SendInput(
            len(events), array_type(*events), ctypes.sizeof(INPUT)
        )
        return sent == len(events)

    def undo(self) -> bool:
        if not self._user32:
            return False
        if self.target_hwnd:
            self._user32.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.04)
        vk_control, vk_z = 0x11, 0x5A
        sequence = (
            INPUT(type=self.INPUT_KEYBOARD, ki=KEYBDINPUT(vk_control, 0, 0, 0, 0)),
            INPUT(type=self.INPUT_KEYBOARD, ki=KEYBDINPUT(vk_z, 0, 0, 0, 0)),
            INPUT(
                type=self.INPUT_KEYBOARD,
                ki=KEYBDINPUT(vk_z, 0, self.KEYEVENTF_KEYUP, 0, 0),
            ),
            INPUT(
                type=self.INPUT_KEYBOARD,
                ki=KEYBDINPUT(vk_control, 0, self.KEYEVENTF_KEYUP, 0, 0),
            ),
        )
        array_type = INPUT * len(sequence)
        sent = self._user32.SendInput(
            len(sequence), array_type(*sequence), ctypes.sizeof(INPUT)
        )
        return sent == len(sequence)

    def press_enter(self, count: int = 1) -> bool:
        if not self._user32:
            return False
        if self.target_hwnd:
            self._user32.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.04)
        events: list[INPUT] = []
        for _ in range(max(1, count)):
            events.append(INPUT(type=self.INPUT_KEYBOARD, ki=KEYBDINPUT(0x0D, 0, 0, 0, 0)))
            events.append(
                INPUT(
                    type=self.INPUT_KEYBOARD,
                    ki=KEYBDINPUT(0x0D, 0, self.KEYEVENTF_KEYUP, 0, 0),
                )
            )
        array_type = INPUT * len(events)
        sent = self._user32.SendInput(
            len(events), array_type(*events), ctypes.sizeof(INPUT)
        )
        return sent == len(events)
