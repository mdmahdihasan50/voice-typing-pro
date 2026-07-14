# Restore the complete project

## Source setup

```bash
git clone https://github.com/mdmahdihasan50/voice-typing-pro.git
cd voice-typing-pro
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

All Python source, GUI code, icons, dependency versions and PyInstaller configuration are committed.

## Rebuild the Windows application

```bash
python build_app.py
```

The generated `build`, `dist` and `__pycache__` directories are intentionally excluded because they are recreated from the committed source. A ready-to-run Windows executable is attached to the GitHub Release.

