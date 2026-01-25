from faster_whisper import WhisperModel
from src.config import config
from src.utils.logger import logger
import traceback

class Transcriber:
    def __init__(self):
        try:
            logger.info(f"Loading Faster-Whisper model '{config.MODEL_SIZE}' on {config.DEVICE}...")
            
            # faster-whisper uses "int8" for CPU, "float16" for GPU
            compute_type = "int8" if config.DEVICE == "cpu" else "float16"
            
            self.model = WhisperModel(
                config.MODEL_SIZE, 
                device=config.DEVICE,
                compute_type=compute_type
            )
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            logger.debug(traceback.format_exc())

    def transcribe(self, audio_path):
        try:
            if not audio_path:
                return ""
            
            logger.debug(f"Transcribing {audio_path}...")
            
            # faster-whisper returns segments iterator
            try:
                # Use initial_prompt to guide model towards Simplified Chinese
                segments, info = self.model.transcribe(
                    audio_path, 
                    language=config.LANGUAGE,
                    beam_size=1,
                    vad_filter=False, # Disabled by default for stability
                    initial_prompt="以下是简体中文的句子。"
                )
                # We need to iterate over segments to trigger the actual transcription
                text_parts = [segment.text for segment in segments]
            except Exception as e:
                if "onnxruntime" in str(e).lower():
                    logger.warning("onnxruntime not found or failing. Retrying without VAD filter...")
                    segments, info = self.model.transcribe(
                        audio_path, 
                        language=config.LANGUAGE,
                        beam_size=1,
                        vad_filter=False, # Disable VAD as fallback
                        initial_prompt="以下是简体中文的句子。"
                    )
                    text_parts = [segment.text for segment in segments]
                else:
                    raise e
            
            # Collect all text
            text = " ".join(text_parts).strip()
            logger.info(f"Transcription result: {text}")
            return text
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            logger.debug(traceback.format_exc())
            return ""
