import os
import sys
from dotenv import load_dotenv

# Load environment variables
if getattr(sys, 'frozen', False):
    # If running as EXE, looks for .env in the internal temp folder
    base_path = sys._MEIPASS
    load_dotenv(os.path.join(base_path, '.env'))
else:
    load_dotenv()

class Config:
    # Hotkey settings
    HOTKEY = "<ctrl>+<cmd>"  # Ctrl + Win key
    
    # Audio settings
    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 1024
    
    # STT Provider Settings
    # Options: "whisper", "sensevoice", "volcengine"
    STT_PROVIDER = "volcengine"
    
    # --- Whisper Settings ---
    # Options: "tiny", "base", "small", "medium", "large-v3"
    # Distilled (Fast & Accurate): "Systran/faster-distil-whisper-large-v3"
    MODEL_SIZE = "small"
    DEVICE = "cpu"           # cpu or cuda
    LANGUAGE = None          # None = Auto-detect language

    # --- Volcengine (Doubao) Settings ---
    # To use this, set STT_PROVIDER = "volcengine"
    VOLC_APP_ID = os.getenv("VOLC_APP_ID")
    VOLC_ACCESS_KEY = os.getenv("VOLC_ACCESS_KEY")
    VOLC_SECRET_KEY = os.getenv("VOLC_SECRET_KEY")
    # Default cluster for ASR
    VOLC_CLUSTER = "volc.bigasr.auc" 

    # --- SenseVoice Settings ---
    # Coming soon in local implementation
    
    # LLM Settings
    LLM_ENABLED = False
    LLM_MODEL = "qwen2:1.5b"
    LLM_API_URL = "http://localhost:11434/api/generate"
    LLM_PROMPT = """你是一个语音输入助手。
请仅移除以下文本中的口语水词（如：那个、嗯、啊、就是、然后、那个什么）。
要求：
1. 保持原句的语气和用词，不要过度修饰。
2. 修正明显的录入错误或重复。
3. 如果原文没有水词，请原样返回。
4. 只返回处理后的结果文本。

文本输入："""

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
        models_dir = os.path.join(Config.BASE_DIR, "models")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

config = Config()
config.ensure_dirs()
