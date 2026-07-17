from __future__ import annotations

import os
import tempfile
import threading
from pathlib import Path

import speech_recognition as sr
from PySide6.QtCore import QObject, Signal


class SpeechEngine(QObject):
    text_recognized = Signal(str)
    state_changed = Signal(str)
    error_occurred = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.language = "bn-BD"
        self.device_index: int | None = None
        self.provider = "google"
        self.offline_model_name = "small"
        self._offline_model = None
        self._offline_loaded_name = ""
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._run_id = 0
        self._lock = threading.RLock()

    @staticmethod
    def input_devices() -> list[tuple[int, str]]:
        audio_interface = None
        try:
            import pyaudio

            audio_interface = pyaudio.PyAudio()
            devices: list[tuple[int, str]] = []
            for index in range(audio_interface.get_device_count()):
                info = audio_interface.get_device_info_by_index(index)
                if int(info.get("maxInputChannels", 0)) > 0:
                    devices.append((index, str(info.get("name", f"Microphone {index}"))))
            return devices
        except Exception:
            return []
        finally:
            if audio_interface is not None:
                audio_interface.terminate()

    @property
    def is_listening(self) -> bool:
        return bool(self._thread and self._thread.is_alive() and not self._stop_event.is_set())

    def configure(
        self,
        *,
        language: str,
        device_index: int | None,
        provider: str,
        offline_model: str,
    ) -> None:
        self.language = language if language in {"bn-BD", "en-US"} else "bn-BD"
        self.device_index = device_index
        self.provider = provider if provider in {"google", "whisper"} else "google"
        self.offline_model_name = (
            offline_model if offline_model in {"tiny", "base", "small"} else "small"
        )

    def start(self) -> None:
        with self._lock:
            if self.is_listening:
                return
            self._run_id += 1
            run_id = self._run_id
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._listen_loop,
                args=(run_id,),
                name="voice-recognition",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            self._run_id += 1
            self._stop_event.set()
        self.state_changed.emit("stopped")

    def shutdown(self) -> None:
        self.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)

    def _is_current(self, run_id: int) -> bool:
        return not self._stop_event.is_set() and run_id == self._run_id

    def _listen_loop(self, run_id: int) -> None:
        try:
            microphone = sr.Microphone(device_index=self.device_index)
            with microphone as source:
                if not self._is_current(run_id):
                    return
                self.state_changed.emit("calibrating")
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.7)
                except Exception:
                    pass
                self.state_changed.emit("listening")

                while self._is_current(run_id):
                    try:
                        audio = self.recognizer.listen(
                            source, timeout=1.0, phrase_time_limit=12
                        )
                    except sr.WaitTimeoutError:
                        continue
                    if not self._is_current(run_id):
                        return
                    self.state_changed.emit("processing")
                    try:
                        text = self._recognize(audio)
                    except sr.UnknownValueError:
                        self.error_occurred.emit("not_understood", "")
                        self.state_changed.emit("listening")
                        continue
                    except sr.RequestError as exc:
                        self.error_occurred.emit("network_error", str(exc))
                        self._stop_event.set()
                        self.state_changed.emit("error")
                        return
                    except Exception as exc:
                        self.error_occurred.emit("error", str(exc))
                        self.state_changed.emit("listening")
                        continue

                    if self._is_current(run_id) and text.strip():
                        self.text_recognized.emit(text.strip())
                    if self._is_current(run_id):
                        self.state_changed.emit("listening")
        except OSError as exc:
            self.error_occurred.emit("no_microphone", str(exc))
            self.state_changed.emit("error")
        except Exception as exc:
            self.error_occurred.emit("error", str(exc))
            self.state_changed.emit("error")
        finally:
            if run_id == self._run_id and not self._stop_event.is_set():
                self._stop_event.set()

    def _recognize(self, audio: sr.AudioData) -> str:
        if self.provider == "whisper":
            return self._recognize_offline(audio)
        return self.recognizer.recognize_google(audio, language=self.language)

    def _recognize_offline(self, audio: sr.AudioData) -> str:
        if self._offline_model is None or self._offline_loaded_name != self.offline_model_name:
            self.state_changed.emit("loading_model")
            from faster_whisper import WhisperModel

            self._offline_model = WhisperModel(
                self.offline_model_name, device="cpu", compute_type="int8"
            )
            self._offline_loaded_name = self.offline_model_name

        handle, name = tempfile.mkstemp(prefix="vtp-", suffix=".wav")
        os.close(handle)
        path = Path(name)
        try:
            path.write_bytes(audio.get_wav_data())
            language = "bn" if self.language.startswith("bn") else "en"
            segments, _ = self._offline_model.transcribe(
                str(path),
                language=language,
                beam_size=5,
                vad_filter=True,
                condition_on_previous_text=False,
            )
            return " ".join(segment.text.strip() for segment in segments).strip()
        finally:
            path.unlink(missing_ok=True)
