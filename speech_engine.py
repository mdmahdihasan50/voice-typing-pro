import speech_recognition as sr
import threading
import time

class SpeechEngine:
    def __init__(self, callback_text, callback_status, callback_error):
        """
        initializes the speech engine.
        :param callback_text: Function to call when text is recognized (str)
        :param callback_status: Function to call when status changes (str)
        :param callback_error: Function to call when an error occurs (str)
        """
        self.recognizer = sr.Recognizer()
        
        # Adjusting dynamic energy threshold ratio might help
        self.recognizer.dynamic_energy_ratio = 1.5
        
        self.is_listening = False
        self.callback_text = callback_text
        self.callback_status = callback_status
        self.callback_error = callback_error
        self.listen_thread = None
        self.language = "en-US" # Default
        self.device_index = None # Default system device
        self.run_id = 0 # To prevent zombie threads

    def get_input_devices(self):
        """Returns a list of available microphone names."""
        return sr.Microphone.list_microphone_names()

    def set_device(self, index):
        """Sets the microphone device index."""
        self.device_index = index
        self.callback_status(f"Mic changed to index {index}")

    def set_language(self, lang_code):
        """
        Sets the language for recognition.
        :param lang_code: 'bn-BD' for Bengali, 'en-US' for English
        """
        self.language = lang_code

    def start_listening(self):
        if self.is_listening:
            return

        self.is_listening = True
        self.run_id += 1 # Increment run ID
        self.callback_status("শুনছি...")
        self.listen_thread = threading.Thread(target=self._listen_loop, args=(self.run_id,), daemon=True)
        self.listen_thread.start()

    def stop_listening(self):
        self.is_listening = False
        self.callback_status("থামানো হয়েছে")

    def _listen_loop(self, my_run_id):
        # Use specific device if selected, else default
        mic = sr.Microphone(device_index=self.device_index)
        
        with mic as source:
            # Adjusting for ambient noise can take a second, 
            # might delay the first listen but improves accuracy.
            if not self.is_listening or self.run_id != my_run_id: return
            
            self.callback_status("মাইক্রোফোন ঠিক করা হচ্ছে...")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            except:
                pass # Continue even if adjust fails
            
            self.callback_status("শুনছি...")
            
            while self.is_listening and self.run_id == my_run_id:
                try:
                    # phrase_time_limit prevents infinite listening if background noise is high
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=10)
                    
                    self.callback_status("প্রসেসিং...")
                    
                    # Recognize speech using Google
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    
                    if text:
                        self.callback_text(text)
                        self.callback_status("শুনছি...")
                        
                except sr.WaitTimeoutError:
                    # No speech detected within timeout, just continue listening
                    continue
                except sr.UnknownValueError:
                    # Audio was not understood
                    # self.callback_error("Could not understand audio")
                    self.callback_status("Listening...") # Just go back to listening
                except sr.RequestError as e:
                    self.callback_error(f"Network error: {e}")
                    self.is_listening = False
                    self.callback_status("Error")
                    break
                except Exception as e:
                    self.callback_error(f"Error: {e}")
                    # self.is_listening = False
                    # break
