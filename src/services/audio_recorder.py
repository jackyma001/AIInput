import pyaudio
import wave
import threading
import os
import numpy as np
from src.config import config
from src.utils.logger import logger

class AudioRecorder:
    def __init__(self, on_audio_level=None):
        self.frames = []
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.on_audio_level = on_audio_level
        self._lock = threading.Lock()

    def start_recording(self):
        try:
            with self._lock:
                if self.is_recording:
                    return
                
                self.frames = []
                self.is_recording = True
                
                self.stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=config.CHANNELS,
                    rate=config.SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=config.CHUNK_SIZE
                )
            
            threading.Thread(target=self._record_loop, daemon=True).start()
            logger.debug("Recording loop thread started.")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False

    def _record_loop(self):
        try:
            while self.is_recording:
                with self._lock:
                    if not self.stream:
                        break
                    try:
                        data = self.stream.read(config.CHUNK_SIZE, exception_on_overflow=False)
                        self.frames.append(data)
                    except Exception as e:
                        logger.error(f"Error reading audio stream: {e}")
                        break
                
                # Calculate audio level for visualization
                if self.on_audio_level:
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    level = np.abs(audio_data).mean() / 32768.0
                    level = min(1.0, level * 30)
                    self.on_audio_level(level)
        except Exception as e:
            logger.error(f"Fatal error in _record_loop: {e}")
        finally:
            logger.debug("Recording loop exited.")

    def stop_recording(self):
        try:
            with self._lock:
                if not self.is_recording:
                    return None
                
                self.is_recording = False
                if self.stream:
                    try:
                        self.stream.stop_stream()
                        self.stream.close()
                    except Exception as e:
                        logger.error(f"Error closing stream: {e}")
                    self.stream = None
            
            logger.debug("Stream stopped and closed.")
            return self._save_to_file()
        except Exception as e:
            logger.error(f"Error in stop_recording: {e}")
            return None

    def _save_to_file(self):
        try:
            filename = os.path.join(config.TEMP_DIR, "output.wav")
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(config.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(config.SAMPLE_RATE)
                wf.writeframes(b''.join(self.frames))
            return filename
        except Exception as e:
            logger.error(f"Error saving audio to file: {e}")
            return None
            
    def __del__(self):
        try:
            self.audio.terminate()
        except:
            pass
