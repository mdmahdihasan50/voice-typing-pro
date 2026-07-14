import customtkinter as ctk
import threading
import webbrowser
import tkinter as tk # Needed for Menu
from PIL import Image
from speech_engine import SpeechEngine
from input_simulator import InputSimulator

class VoiceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # System Settings
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Window Config
        self.title("ভয়েস টাইপিং প্রো ফর হাফেজ মাহদী হাসান")
        self.geometry("900x600")
        self.resizable(False, False)

        # Logic Modules
        self.input_sim = InputSimulator()
        self.speech_engine = SpeechEngine(
            callback_text=self.on_text_recognized,
            callback_status=self.update_status,
            callback_error=self.update_status  # Show errors in status line
        )
        
        # State
        self.is_listening = False
        self.mode = "Internal" # "Internal" or "Global"
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.create_main_area()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="ভয়েস টাইপিং\nপ্রো", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Language Toggle Button
        self.lang_var = "ইংরেজি" # Default (Matches Engine "en-US")
        self.lang_btn = ctk.CTkButton(self.sidebar_frame, text="ভাষা: ইংরেজি", command=self.toggle_language,
                                      fg_color="#3B8ED0", hover_color="#1F6AA5")
        self.lang_btn.grid(row=2, column=0, padx=20, pady=(10, 20))

        # Mode Selection
        self.mode_label = ctk.CTkLabel(self.sidebar_frame, text="টাইপিং মোড", anchor="w")
        self.mode_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        
        self.mode_switch = ctk.CTkSwitch(self.sidebar_frame, text="গ্লোবাল টাইপিং", command=self.toggle_mode)
        self.mode_switch.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="n")

        # Always on Top
        self.top_switch = ctk.CTkSwitch(self.sidebar_frame, text="সবার উপরে রাখুন", command=self.toggle_top)
        self.top_switch.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="s")

        # Mic Selection
        self.mic_label = ctk.CTkLabel(self.sidebar_frame, text="মাইক্রোফোন", anchor="w")
        self.mic_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        
        self.available_mics = self.speech_engine.get_input_devices()
        # Filter for unique names or just show all with index
        self.mic_names = [f"{i}: {name}" for i, name in enumerate(self.available_mics)]
        
        self.mic_var = ctk.StringVar(value=self.mic_names[0] if self.mic_names else "Default")
        self.mic_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=self.mic_names,
                                         command=self.change_mic, variable=self.mic_var, 
                                         dynamic_resizing=False, width=160)
        self.mic_menu.grid(row=7, column=0, padx=20, pady=(10, 20))

        # Developer Info
        self.dev_label = ctk.CTkLabel(self.sidebar_frame, text="ডেভেলপার:", anchor="w", font=ctk.CTkFont(size=12, weight="bold"))
        self.dev_label.grid(row=8, column=0, padx=20, pady=(20, 0))

        # Load Icon
        try:
            fb_img = ctk.CTkImage(light_image=Image.open("fb_icon.png"), 
                                  dark_image=Image.open("fb_icon.png"), 
                                  size=(20, 20))
        except:
            fb_img = None

        self.fb_btn = ctk.CTkButton(self.sidebar_frame, text="হাফেজ মাহাদী হাসান (FB)", 
                                    command=self.open_facebook,
                                    fg_color="#1877F2", hover_color="#145dbf", # Facebook Blue
                                    image=fb_img, compound="right", # Icon on right
                                    height=35)
        self.fb_btn.grid(row=9, column=0, padx=20, pady=(5, 20))

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Status
        self.status_label = ctk.CTkLabel(self.main_frame, text="টাইপ করার জন্য প্রস্তুত...", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")

        # Text Area (Internal Pad)
        self.textbox = ctk.CTkTextbox(self.main_frame, width=600, height=350, 
                                      font=ctk.CTkFont(family="Consolas", size=18),
                                      fg_color=("gray95", "#2B2B2B"),
                                      border_width=2, border_color="#3B8ED0", # Blue border for focus
                                      undo=True) # Enable Undo/Redo
        self.textbox.grid(row=1, column=0, padx=30, pady=(10, 5), sticky="nsew")
        self.textbox.insert("0.0", "কিছু বলুন...\n")
        self.textbox.bind("<KeyRelease>", self.update_counts) # Update count on typing
        self.textbox.bind("<Button-3>", self.do_popup) # Right click menu

        # Context Menu
        self.menu = tk.Menu(self, tearoff=0)
        # We must access the internal _textbox to trigger standard Tkinter events correctly
        self.menu.add_command(label="কাট (Cut)", command=lambda: self.textbox._textbox.event_generate("<<Cut>>"))
        self.menu.add_command(label="কপি (Copy)", command=lambda: self.textbox._textbox.event_generate("<<Copy>>"))
        self.menu.add_command(label="পেস্ট (Paste)", command=lambda: self.textbox._textbox.event_generate("<<Paste>>"))
        self.menu.add_separator()
        self.menu.add_command(label="সব সিলেক্ট (Select All)", command=self.select_all)

        # Status Bar & Counts
        self.info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=30)
        self.info_frame.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="ew")
        
        self.count_label = ctk.CTkLabel(self.info_frame, text="শব্দ: 0 | অক্ষর: 0", text_color="gray70")
        self.count_label.pack(side="right")

        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.grid(row=3, column=0, pady=10, sticky="ew")
        self.btn_frame.grid_columnconfigure(0, weight=1) # Spacer left
        self.btn_frame.grid_columnconfigure(3, weight=1) # Spacer right

        # Left Side (Clear & Copy)
        self.clear_btn = ctk.CTkButton(self.btn_frame, text="🗑️ মুছুন", height=50, width=120,
                                       font=ctk.CTkFont(size=16, weight="bold"),
                                       corner_radius=25, command=self.clear_text,
                                       fg_color="#D03B3B", hover_color="#A51F1F")
        self.clear_btn.grid(row=0, column=1, padx=10, sticky="w")

        self.copy_btn = ctk.CTkButton(self.btn_frame, text="📋 কপি", height=50, width=120,
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      corner_radius=25, command=self.copy_text,
                                      fg_color="#3B8ED0", hover_color="#1F6AA5")
        self.copy_btn.grid(row=0, column=2, padx=10, sticky="w")
        
        self.save_btn = ctk.CTkButton(self.btn_frame, text="💾 সেভ", height=50, width=120,
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      corner_radius=25, command=self.save_text,
                                      fg_color="#F39C12", hover_color="#D68910") # Orange
        self.save_btn.grid(row=0, column=3, padx=10, sticky="w")
        
        # Right Side (Mic) - Using a spacer to push it
        self.mic_btn = ctk.CTkButton(self.btn_frame, text="🎤 শুরু করুন", height=50, width=200, 
                                     font=ctk.CTkFont(size=18, weight="bold"),
                                     corner_radius=25, command=self.toggle_listening,
                                     fg_color="#00A86B", hover_color="#008f5b") # Modern Green
        self.mic_btn.grid(row=0, column=5, padx=10, sticky="e")

    def update_counts(self, event=None):
        text = self.textbox.get("0.0", "end").strip()
        words = len(text.split())
        chars = len(text)
        self.count_label.configure(text=f"শব্দ: {words} | অক্ষর: {chars}")

    def do_popup(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def select_all(self):
        self.textbox.tag_add("sel", "0.0", "end")
        self.textbox.focus_set()

    def save_text(self):
        text = self.textbox.get("0.0", "end").strip()
        if not text:
            self.update_status("সেভ করার মতো কিছু নেই!")
            return
            
        file_path = ctk.filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
                                                     title="সেভ করুন")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.update_status("সফলভাবে সেভ করা হয়েছে!")
            except Exception as e:
                self.update_status(f"ভুল হয়েছে: {e}")

    def copy_text(self):
        text = self.textbox.get("0.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update_status("ক্লিপবোর্ডে কপি করা হয়েছে!")
            self.after(2000, lambda: self.update_status("প্রস্তুত"))

    def clear_text(self):
        self.textbox.delete("0.0", "end")
        self.update_status("লেখা মুছে ফেলা হয়েছে।")

    def open_facebook(self):
        webbrowser.open("https://www.facebook.com/hafezmahdihasan50")
        
    def toggle_language(self):
        if self.lang_var == "বাংলা":
            self.lang_var = "ইংরেজি"
            self.speech_engine.set_language("en-US")
            self.lang_btn.configure(text="Language: English")
        else:
            self.lang_var = "বাংলা"
            self.speech_engine.set_language("bn-BD")
            self.lang_btn.configure(text="ভাষা: বাংলা")

    def change_mic(self, choice):
        # Extract index from string "Index: Name"
        try:
            index = int(choice.split(":")[0])
            self.speech_engine.set_device(index)
            # If already listening, we might need to restart? 
            # For now, let's just let it take effect on next listen or rely on engine (engine restart might be needed if running)
            if self.is_listening:
                self.speech_engine.stop_listening()
                self.status_label.configure(text="Restarting listener with new Mic...")
                self.after(1000, lambda: self.toggle_listening()) # Toggle back on
                self.toggle_listening() # Toggle off logic handled above
        except Exception as e:
            print(f"Error changing mic: {e}")
            
    def toggle_mode(self):
        if self.mode_switch.get() == 1:
            self.mode = "Global"
            self.textbox.configure(state="disabled", fg_color="gray20") # Dim the text box
            self.status_label.configure(text="অ্যাক্টিভ: অন্য অ্যাপে কার্সার রাখুন")
        else:
            self.mode = "Internal"
            self.textbox.configure(state="normal", fg_color=("gray100", "gray20")) 
            self.textbox.configure(fg_color=["#F9F9FA", "#1D1E1E"]) 
            self.status_label.configure(text="ইন্টারনাল মোড: নিচে টাইপ হচ্ছে")

    def toggle_top(self):
        if self.top_switch.get() == 1:
            self.attributes('-topmost', True)
        else:
            self.attributes('-topmost', False)

    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.mic_btn.configure(text="🛑 থামুন", fg_color="#D03B3B", hover_color="#A51F1F")
            self.speech_engine.start_listening()
        else:
            self.is_listening = False
            self.mic_btn.configure(text="🎤 শুরু করুন", fg_color="#00A86B", hover_color="#008f5b")
            self.speech_engine.stop_listening()

    def update_status(self, status_text):
        # Update UI thread safe
        self.status_label.configure(text=status_text)
        self.update_idletasks()

    def on_text_recognized(self, text):
        if self.mode == "Internal":
            self.textbox.insert("end", text + " ")
            self.textbox.see("end")
            self.update_counts()
        else:
            # InputSimulator handles the space at the end already
            self.input_sim.type_text(text)
