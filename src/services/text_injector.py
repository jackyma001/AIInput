import time
import sys
import pyperclip
from pynput.keyboard import Controller, Key
from src.utils.logger import logger

class TextInjector:
    def __init__(self):
        self.keyboard = Controller()

    def type_text(self, text):
        if not text:
            return
        
        try:
            logger.info(f"Injecting text via Clipboard: {text}")
            
            # 1. Backup current clipboard
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                original_clipboard = ""
            
            # 2. Copy new text to clipboard
            pyperclip.copy(text)
            
            # 3. Short wait to ensure clipboard update
            time.sleep(0.1) 
            
            # 4. Simulate Paste command (Cmd+V on macOS, Ctrl+V on others)
            paste_key = Key.cmd if sys.platform == 'darwin' else Key.ctrl
            with self.keyboard.pressed(paste_key):
                self.keyboard.press('v')
                self.keyboard.release('v')
            
            logger.debug("Clipboard paste command sent.")

            # 5. Restore original clipboard (delayed to allow paste to finish)
            # We use a slight delay so the paste has time to be read by the target app
            time.sleep(0.5)
            pyperclip.copy(original_clipboard)
            logger.debug("Clipboard restored.")
            
        except Exception as e:
            logger.error(f"Error during text injection: {e}")
