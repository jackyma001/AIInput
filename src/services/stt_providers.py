import os
import json
import uuid
import threading
import time
import traceback
import gzip
import struct
from abc import ABC, abstractmethod
from src.utils.logger import logger

class BaseSTTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass

class WhisperProvider(BaseSTTProvider):
    def __init__(self, config):
        from faster_whisper import WhisperModel
        self.config = config
        model_path = self._download_if_needed(config.MODEL_SIZE)
        compute_type = "int8" if config.DEVICE == "cpu" else "float16"
        logger.info(f"Loading Faster-Whisper model '{config.MODEL_SIZE}' on {config.DEVICE}...")
        self.model = WhisperModel(model_path, device=config.DEVICE, compute_type=compute_type)

    def _download_if_needed(self, model_input):
        import huggingface_hub
        if "/" in model_input and not os.path.exists(model_input):
            try:
                local_name = model_input.replace("/", "--")
                local_path = os.path.join(self.config.BASE_DIR, "models", local_name)
                if os.path.exists(local_path): return local_path
                downloaded_path = huggingface_hub.snapshot_download(repo_id=model_input, local_dir=local_path, local_dir_use_symlinks=False)
                return downloaded_path
            except Exception: return model_input
        return model_input

    def transcribe(self, audio_path):
        segments, _ = self.model.transcribe(audio_path, language=self.config.LANGUAGE, vad_filter=True)
        return " ".join([s.text for s in segments]).strip()

class VolcengineProvider(BaseSTTProvider):
    """
    Volcengine (Doubao) Streaming ASR Provider.
    Uses WebSocket binary protocol for real-time speech recognition.
    """
    def __init__(self, config):
        self.config = config
        self.appid = config.VOLC_APP_ID
        self.token = config.VOLC_ACCESS_KEY
        self.cluster = config.VOLC_CLUSTER

    def transcribe(self, audio_path):
        if not self.appid: 
            return "(火山引擎 AppID 未配置)"
        
        # Flash/Turbo API is the only one supporting Base64 upload for Big Model
        return self._transcribe_flash(audio_path)

    def _transcribe_flash(self, audio_path):
        """
        Volcengine Flash (Turbo) API.
        Endpoint: /api/v3/auc/bigmodel/recognize/flash
        Resource ID: volc.bigasr.auc_turbo
        Supports: Base64 audio upload (audio.data).
        """
        import requests
        import base64
        import uuid
        
        url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
        req_id = str(uuid.uuid4())
        
        # Flash API requires this specific resource ID
        resource_id = "volc.bigasr.auc_turbo"
        
        headers = {
            "X-Api-App-Key": self.appid,
            "X-Api-Access-Key": self.token,
            "X-Api-Resource-Id": resource_id,
            "X-Api-Request-Id": req_id,
            "X-Api-Sequence": "-1",
            "Content-Type": "application/json"
        }
        
        try:
            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            payload = {
                "user": {"uid": "aiinput_user"},
                "audio": {
                    "format": "wav",
                    "rate": 16000,
                    "bits": 16,
                    "channel": 1,
                    # Flash API specifically supports 'data' for Base64
                    "data": audio_base64
                },
                "request": {
                    "model_name": "bigmodel",
                    "enable_itn": True,
                    "enable_punc": True,
                    "reqid": req_id
                }
            }
            
            logger.info(f"Volc Flash Request: {req_id}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Check headers for API status
            status_code = response.headers.get("X-Api-Status-Code", "")
            if status_code != "20000000":
                api_msg = response.headers.get("X-Api-Message", "Unknown Error")
                # Specific hint for the most common error
                if "requested resource not granted" in api_msg:
                    return f"(Please Enable 'Flash/Turbo' in Console! Error: {api_msg})"
                return f"(Volc Flash Error [{status_code}]: {api_msg})"
            
            res_json = response.json()
            if "result" in res_json and "text" in res_json["result"]:
                return res_json["result"]["text"]
            
            return f"(Volc Flash: No text. Response: {res_json})"

        except Exception as e:
            logger.error(f"Volcengine Flash error: {e}")
            return f"(Request Error: {e})"

def get_provider(config):
    if config.STT_PROVIDER == "volcengine":
        return VolcengineProvider(config)
    elif config.STT_PROVIDER == "sensevoice":
        return SenseVoiceProvider(config)
    else:
        return WhisperProvider(config)

class SenseVoiceProvider(BaseSTTProvider):
    def __init__(self, config):
        self.config = config
        logger.info("SenseVoiceSmall (ONNX) is ready to be implemented locally.")
    def transcribe(self, audio_path):
        return "(SenseVoice 引擎集成中，建议先使用 volcengine 模式体验高精度)"
