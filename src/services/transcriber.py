from faster_whisper import WhisperModel
from src.config import config
from src.utils.logger import logger
import traceback
import os
import huggingface_hub

class Transcriber:
    def __init__(self):
        try:
            logger.info(f"Loading Faster-Whisper model '{config.MODEL_SIZE}' on {config.DEVICE}...")
            
            # fast-path: Check if model needs explicit download (solving WinError 1314)
            model_path = self._download_if_needed(config.MODEL_SIZE)
            
            # faster-whisper uses "int8" for CPU, "float16" for GPU
            compute_type = "int8" if config.DEVICE == "cpu" else "float16"
            
            self.model = WhisperModel(
                model_path, 
                device=config.DEVICE,
                compute_type=compute_type
            )
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            logger.debug(traceback.format_exc())

    def _download_if_needed(self, model_input):
        """
        Robust downloader that avoids symlinks on Windows (fixing WinError 1314).
        If model_input contains '/' (e.g. 'Systran/faster-distil-whisper-large-v3'),
        we manually download it to a local folder without symlinks.
        """
        if "/" in model_input and not os.path.exists(model_input):
            try:
                # Construct a safe local path (replacing / with _)
                local_name = model_input.replace("/", "--")
                local_path = os.path.join(config.BASE_DIR, "models", local_name)
                
                logger.info(f"Checking/Downloading model '{model_input}' to '{local_path}' (No Symlinks)...")
                
                # Check if already exists to save time (huggingface handles this but lets be explicit)
                # We use snapshot_download with local_dir_use_symlinks=False
                downloaded_path = huggingface_hub.snapshot_download(
                    repo_id=model_input,
                    local_dir=local_path,
                    local_dir_use_symlinks=False  # CRITICAL: Fix for WinError 1314
                )
                logger.info(f"Model available at: {downloaded_path}")
                return downloaded_path
            except Exception as e:
                logger.warning(f"Manual download failed: {e}. Falling back to default loader.")
                return model_input
        return model_input

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
                    vad_filter=True,  # Enable VAD to filter silence (Speedup!)
                    vad_parameters=dict(min_silence_duration_ms=500),
                    # initial_prompt="以下是简体中文的句子。" # REMOVED: Allow auto-detect for English/Chinese mixed
                )
                # We need to iterate over segments to trigger the actual transcription
                text_parts = [segment.text for segment in segments]
            except Exception as e:
                # Log the actual error to debug "onnxruntime" issues
                if "onnxruntime" in str(e).lower():
                    logger.error(f"VAD Failure Detailed Error: {e}")
                    logger.warning("onnxruntime not found or failing. Retrying without VAD filter...")
                    segments, info = self.model.transcribe(
                        audio_path, 
                        language=config.LANGUAGE,
                        beam_size=1,
                        vad_filter=False, # Disable VAD as fallback
                        # initial_prompt="以下是简体中文的句子。" # REMOVED
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
