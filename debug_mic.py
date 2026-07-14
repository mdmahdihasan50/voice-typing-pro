import speech_recognition as sr
import pyaudio

print("--- Starting Diagnostic ---")

# Check PyAudio
try:
    p = pyaudio.PyAudio()
    print(f"PyAudio initialized. API count: {p.get_host_api_count()}")
    info = p.get_host_api_info_by_index(0)
    print(f"Default Host API info: {info}")
except Exception as e:
    print(f"PyAudio Error: {e}")

# Check Microphones
print("\n--- Available Microphones ---")
try:
    mics = sr.Microphone.list_microphone_names()
    for i, mic_name in enumerate(mics):
        print(f"Mic {i}: {mic_name}")
except Exception as e:
    print(f"Error listing mics: {e}")

# Test Listening
print("\n--- Testing Recognition (5s limit) ---")
r = sr.Recognizer()
try:
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... (Please wait)")
        r.adjust_for_ambient_noise(source, duration=1)
        print(f"Energy threshold: {r.energy_threshold}")
        print("Listening now... Speak something!")
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        print("Audio captured. Recognizing...")
        try:
            text = r.recognize_google(audio)
            print(f"SUCCESS! Recognized: '{text}'")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
except Exception as e:
    print(f"CRITICAL ERROR during listening: {e}")

print("--- Diagnostic Finished ---")
