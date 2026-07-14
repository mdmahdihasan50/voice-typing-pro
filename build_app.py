import PyInstaller.__main__
import customtkinter
import os

# Get customtkinter path to include data files (json, fonts, etc.)
ctk_path = os.path.dirname(customtkinter.__file__)
print(f"CustomTkinter path: {ctk_path}")

# Build command arguments
args = [
    'main.py',                  # Main script
    '--name=VoiceTypingPro',    # Name of the exe
    '--onefile',                # Single exe file
    '--noconsole',              # No black console window
    '--windowed',               # Windowed mode
    f'--add-data={ctk_path};customtkinter', # Include CTK assets
    '--add-data=fb_icon.png;.',             # Include FB Icon (source;dest)
    '--clean',                  # Clean cache
    '--icon=NONE'               # No app icon
]

print("Starting build process...")
PyInstaller.__main__.run(args)
print("Build finished!")
