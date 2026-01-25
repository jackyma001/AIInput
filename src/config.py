import os
import sys

class Config:
    # Hotkey settings
    HOTKEY = "<ctrl>+<cmd>"  # Ctrl + Win key
    
    # Audio settings
    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 1024
    
    # Model settings
    MODEL_SIZE = "small"      # tiny=fastest, base, small, medium, large=slowest
    DEVICE = "cpu"           # cpu or cuda (for NVIDIA GPU)
    LANGUAGE = "zh"          # Set to Chinese for faster detection

    # Paths
    if getattr(sys, 'frozen', False):
        # Running as EXE
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # Running as script
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    TEMP_DIR = os.path.join(BASE_DIR, "temp")
    LOG_FILE = os.path.join(BASE_DIR, "app.log")

    @staticmethod
    def ensure_dirs():
        if not os.path.exists(Config.TEMP_DIR):
            os.makedirs(Config.TEMP_DIR)

config = Config()
config.ensure_dirs()
