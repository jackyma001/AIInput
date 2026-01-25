import requests
import json
from src.config import config
from src.utils.logger import logger

class LLMRefiner:
    def __init__(self):
        self.enabled = config.LLM_ENABLED
        self.api_url = config.LLM_API_URL
        self.model = config.LLM_MODEL
        self.prompt_template = config.LLM_PROMPT

    def refine(self, text):
        if not self.enabled or not text.strip():
            return text

        logger.debug(f"Refining text via LLM: {text}")
        
        payload = {
            "model": self.model,
            "prompt": f"{self.prompt_template}{text}",
            "stream": False,
            "options": {
                "temperature": 0.3, # Low temperature for more consistent results
                "num_predict": 100  # Usually enough for a single response
            }
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            refined_text = result.get("response", "").strip()
            
            if refined_text:
                logger.info(f"Refined Text: {refined_text}")
                return refined_text
            else:
                logger.warning("LLM returned empty response, using original text.")
                return text
        except Exception as e:
            logger.error(f"LLM Refining failed: {e}")
            return text
