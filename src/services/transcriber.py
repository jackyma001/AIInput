from src.config import config
from src.utils.logger import logger
from src.services.stt_providers import get_provider
import traceback

class Transcriber:
    def __init__(self):
        try:
            logger.info(f"Initializing STT Engine: {config.STT_PROVIDER}...")
            self.provider = get_provider(config)
            logger.info(f"STT Engine '{config.STT_PROVIDER}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load STT Engine: {e}")
            logger.debug(traceback.format_exc())
            self.provider = None

    def transcribe(self, audio_path):
        try:
            if not audio_path:
                return ""
            
            if not self.provider:
                logger.error("No STT provider available.")
                return ""

            text = self.provider.transcribe(audio_path)
            logger.info(f"Transcription result: {text}")
            return text
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            logger.debug(traceback.format_exc())
            return ""
