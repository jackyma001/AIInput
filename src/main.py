import sys
import os
import traceback
from datetime import datetime

# CRITICAL: Setup global exception handler immediately to catch import errors
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Try to log to a file even if logger isn't ready
    try:
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        with open("crash_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] CRITICAL CRASH:\n{error_msg}\n")
    except:
        pass # If we can't write to file, we're really in trouble

    # Also try to use the app logger if available
    try:
        from src.utils.logger import logger
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    except:
        pass

sys.excepthook = handle_exception

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

# Add project root to sys.path to allow imports from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Imports with logging available (handled by excepthook)
from src.services.hotkey_manager import HotkeyManager
from src.ui.tray_icon import TrayIcon
from src.ui.listening_bar import ListeningBar
from src.utils.logger import logger

class AppSignals(QObject):
    """Signals to communicate from background threads to UI"""
    show_bar = pyqtSignal()
    hide_bar = pyqtSignal()
    update_level = pyqtSignal(float)
    update_tray = pyqtSignal(bool)

def main():
    if sys.platform.startswith('win'):
        import multiprocessing
        multiprocessing.freeze_support()

    app = QApplication(sys.argv)
    # Ensure app doesn't exit when window is hidden
    app.setQuitOnLastWindowClosed(False)
    
    logger.info("Initializing AIInput (Unified PyQt5 Loop)...")
    
    # UI Components
    listening_bar = ListeningBar()
    signals = AppSignals()
    
    # Connect signals (Background -> UI)
    signals.show_bar.connect(listening_bar.show_bar)
    signals.hide_bar.connect(listening_bar.hide_bar)
    signals.update_level.connect(listening_bar.update_audio_level)
    
    # We'll initialize tray later to pass the manager
    
    # Define callbacks for HotkeyManager (which runs in background)
    def on_start():
        signals.show_bar.emit()
        signals.update_tray.emit(True)

    def on_stop():
        signals.hide_bar.emit()
        signals.update_tray.emit(False)
    
    def on_audio_level(level):
        signals.update_level.emit(level)

    manager = HotkeyManager(
        on_recording_start=on_start, 
        on_recording_stop=on_stop,
        on_audio_level=on_audio_level
    )
    
    tray = TrayIcon(manager, listening_bar)
    signals.update_tray.connect(tray.update_status)
    
    # Start listening
    manager.start_listening()
    
    logger.info("Application started. Unified UI loop running.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
