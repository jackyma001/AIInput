from pynput import keyboard
import threading
from src.config import config
from src.services.audio_recorder import AudioRecorder
from src.services.transcriber import Transcriber
from src.services.text_injector import TextInjector
from src.utils.logger import logger
import winsound
import traceback

class HotkeyManager:
    def __init__(self, on_recording_start=None, on_recording_stop=None, on_audio_level=None):
        self.on_audio_level = on_audio_level
        self.recorder = AudioRecorder(on_audio_level=on_audio_level)
        self.transcriber = Transcriber()
        self.injector = TextInjector()
        self.on_recording_start = on_recording_start
        self.on_recording_stop = on_recording_stop
        
        # Track pressed keys for push-to-talk
        self.pressed_keys = set()
        self.hotkey_active = False
        self.listener = None
        self.is_listening = False

    def start_listening(self):
        self.is_listening = True
        # Use regular keyboard listener for press/release events
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        logger.info("Hotkey listener started (Ctrl + Win).")

    def stop_listening(self):
        self.is_listening = False
        if self.listener:
            self.listener.stop()
        logger.info("Hotkey listener stopped.")

    def _on_press(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.pressed_keys.add('ctrl')
            elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_r:
                self.pressed_keys.add('cmd')
        except Exception as e:
            logger.error(f"Error in _on_press: {e}")
        
        # Check if hotkey combo is pressed
        if 'ctrl' in self.pressed_keys and 'cmd' in self.pressed_keys:
            if not self.hotkey_active:
                self.hotkey_active = True
                self._start_recording()

    def _on_release(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.pressed_keys.discard('ctrl')
            elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_r:
                self.pressed_keys.discard('cmd')
        except Exception as e:
            logger.error(f"Error in _on_release: {e}")
        
        # If hotkey was active and now one of the keys is released, stop recording
        if self.hotkey_active:
            if 'ctrl' not in self.pressed_keys or 'cmd' not in self.pressed_keys:
                self.hotkey_active = False
                self._stop_recording()

    def _start_recording(self):
        try:
            if not self.recorder.is_recording:
                logger.debug("Hotkey combo pressed: Starting recording")
                self.recorder.start_recording()
                # Play a very short, subtle beep (low frequency, short duration)
                threading.Thread(target=lambda: winsound.Beep(600, 50), daemon=True).start()
                if self.on_recording_start:
                    self.on_recording_start()
        except Exception as e:
            logger.error(f"Error starting recording via hotkey: {e}")

    def _stop_recording(self):
        try:
            if self.recorder.is_recording:
                logger.debug("Hotkey combo released: Stopping recording")
                audio_file = self.recorder.stop_recording()
                if self.on_recording_stop:
                    self.on_recording_stop()
                
                if audio_file:
                    threading.Thread(target=self._process_audio, args=(audio_file,), daemon=True).start()
        except Exception as e:
            logger.error(f"Error stopping recording via hotkey: {e}")

    def _process_audio(self, audio_file):
        try:
            text = self.transcriber.transcribe(audio_file)
            if text:
                self.injector.type_text(text)
        except Exception as e:
            logger.error(f"Error processing audio in thread: {e}")
            logger.debug(traceback.format_exc())
