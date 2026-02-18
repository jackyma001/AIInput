from pynput import keyboard
import threading
from src.config import config
from src.services.audio_recorder import AudioRecorder
from src.services.transcriber import Transcriber
from src.services.text_injector import TextInjector
from src.services.llm_refiner import LLMRefiner
from src.utils.logger import logger
import sys
import os
import traceback

class HotkeyManager:
    def __init__(self, on_recording_start=None, on_recording_stop=None, on_audio_level=None):
        self.on_audio_level = on_audio_level
        self.recorder = AudioRecorder(on_audio_level=on_audio_level)
        self.transcriber = None
        self.injector = TextInjector()
        self.refiner = LLMRefiner()
        self.on_recording_start = on_recording_start
        self.on_recording_stop = on_recording_stop
        
        # Async model loading
        threading.Thread(target=self._load_transcriber, daemon=True).start()
        
        # Track pressed keys for push-to-talk
        self.pressed_keys = set()
        self.hotkey_active = False
        self.listener = None
        self.is_listening = False

    def _load_transcriber(self):
        try:
            self.transcriber = Transcriber()
        except Exception as e:
            logger.error(f"Failed to load transcriber: {e}")

    def start_listening(self):
        self.is_listening = True
        # Use regular keyboard listener for press/release events
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        logger.info("Hotkey listener started (Ctrl + Shift).")

    def stop_listening(self):
        self.is_listening = False
        if self.listener:
            self.listener.stop()
        logger.info("Hotkey listener stopped.")

    def _on_press(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.pressed_keys.add('ctrl')
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self.pressed_keys.add('shift')
        except Exception as e:
            logger.error(f"Error in _on_press: {e}")
        
        # Check if hotkey combo is pressed
        if 'ctrl' in self.pressed_keys and 'shift' in self.pressed_keys:
            if not self.hotkey_active:
                self.hotkey_active = True
                self._start_recording()

    def _on_release(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.pressed_keys.discard('ctrl')
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self.pressed_keys.discard('shift')
        except Exception as e:
            logger.error(f"Error in _on_release: {e}")
        
        # If hotkey was active and now one of the keys is released, stop recording
        if self.hotkey_active:
            if 'ctrl' not in self.pressed_keys or 'shift' not in self.pressed_keys:
                self.hotkey_active = False
                self._stop_recording()

    def _start_recording(self):
        try:
            if not self.recorder.is_recording:
                logger.debug("Hotkey combo pressed: Starting recording")
                self.recorder.start_recording()
                # Play a short, subtle notification
                if sys.platform == 'win32':
                    import winsound
                    threading.Thread(target=lambda: winsound.Beep(600, 50), daemon=True).start()
                elif sys.platform == 'darwin':
                    # macOS system beep
                    threading.Thread(target=lambda: os.system('echo -e "\a"'), daemon=True).start()
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
            if not self.transcriber:
                logger.warning("Transcriber still loading...")
                self.injector.type_text("(AI模型正在加载中，请稍后再试...)")
                return

            text = self.transcriber.transcribe(audio_file)
            if text:
                # Refine text if enabled
                refined_text = self.refiner.refine(text)
                self.injector.type_text(refined_text)
        except Exception as e:
            logger.error(f"Error processing audio in thread: {e}")
            logger.debug(traceback.format_exc())
