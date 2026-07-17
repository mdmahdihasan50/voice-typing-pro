# বাংলা ভয়েস টাইপিং প্রো 2.1.1

বাংলা ভয়েস টাইপিং প্রো is a Windows desktop dictation assistant for Bengali and English. Bengali is the default. It includes a modern writing pad, built-in help center and a compact always-on-top bar that can type into Word, browsers, messaging apps and other standard Windows text fields.

## Highlights

- Complete Bengali and English interface; Bengali defaults for UI and dictation
- Online Google recognition and optional offline Faster Whisper recognition
- Internal writing pad and global typing into the previously active application
- Draggable no-focus floating voice bar, system tray and remembered position
- Global shortcuts and F9 push-to-talk mode
- Bengali/English punctuation and editing voice commands
- Auto-save and crash recovery, recent files and dictation history
- Find/replace, word/character and cursor counts, editor zoom and themes
- UTF-8 TXT/Markdown save plus DOCX and PDF export
- Microphone, model, font, startup and privacy-friendly local settings

## Keyboard shortcuts

| Action | Shortcut |
|---|---|
| Start/stop dictation | `Ctrl+Shift+Space` |
| Hold to talk (when enabled) | `F9` |
| Bengali dictation | `Alt+Shift+B` |
| English dictation | `Alt+Shift+E` |
| Find/replace | `Ctrl+F` |
| Settings | `Ctrl+,` |

## Voice commands

Commands are recognized when spoken as a complete phrase.

- `নতুন লাইন`, `নতুন প্যারাগ্রাফ`
- `শেষ শব্দ মুছুন`, `শেষ বাক্য মুছুন`, `সব মুছুন`
- `বাংলা মোড`, `ইংরেজি মোড`, `টাইপিং বন্ধ`
- `কমা`, `দাঁড়ি`, `প্রশ্নবোধক চিহ্ন`, `বিস্ময়বোধক চিহ্ন`
- English equivalents such as `new line`, `delete last word`, `comma`, `full stop`

## Development setup

Python 3.12 is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe main.py
```

The first use of offline Whisper downloads the selected `tiny`, `base` or `small` model. Models are stored in the normal Hugging Face cache and are not bundled in the repository.

## Test and build

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe build_app.py
```

The executable is written to `dist\BanglaVoiceTypingPro.exe`. The Inno Setup definition in `installer\VoiceTypingPro.iss` creates a per-user Windows installer with optional startup and desktop shortcuts.

## Global typing notes

Global text uses native Windows Unicode `SendInput`, so Bengali conjuncts do not depend on an installed keyboard layout. Windows does not allow a normal application to inject text into an application running as Administrator; run both at the same privilege level when needed.

Settings, recovery text and history are kept locally in the user's application-data folders. Audio is sent to Google only when the online engine is selected. The Whisper option processes captured audio locally after its model has been downloaded.

The bundled Noto Sans Bengali font is distributed under the SIL Open Font License 1.1; the license text is included beside the font in `voice_typing_pro/assets/fonts`.
