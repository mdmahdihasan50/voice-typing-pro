# Restore and rebuild বাংলা ভয়েস টাইপিং প্রো

```powershell
git clone https://github.com/mdmahdihasan50/voice-typing-pro.git
cd voice-typing-pro
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe main.py
```

Build the standalone Windows executable with:

```powershell
.\.venv\Scripts\python.exe build_app.py
```

If Inno Setup is installed, open `installer\VoiceTypingPro.iss` or run `ISCC.exe installer\VoiceTypingPro.iss` after the executable build finishes.

The `build`, `dist`, `.venv`, caches, downloaded Whisper models and user settings are generated locally and are intentionally not committed.
