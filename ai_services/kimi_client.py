"""
Kimi API Client
Lightweight OpenAI-compatible client for Moonshot AI (Kimi).
"""
import json
import logging
from typing import List, Dict, Any, Optional

import requests

from . import config

logger = logging.getLogger(__name__)


class KimiClient:
    """
    Thin wrapper around Kimi's OpenAI-compatible chat completions API.
    Can be swapped for OpenAI, Anthropic, or local models in the future
    without changing service-layer code.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or config.KIMI_API_KEY
        self.base_url = (base_url or config.KIMI_API_BASE).rstrip('/')
        self.model = model or config.KIMI_MODEL
        self.timeout = config.AI_REQUEST_TIMEOUT

        if not self.api_key:
            logger.warning("KimiClient initialized without API key — calls will fail.")

    # ── Public API ─────────────────────────────────────────────────

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request.
        Returns the parsed JSON response or raises on failure.
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else config.DEFAULT_TEMPERATURE,
            "max_tokens": max_tokens if max_tokens is not None else config.DEFAULT_MAX_TOKENS,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        logger.debug(f"[KimiClient] POST {url} model={self.model} msgs={len(messages)}")

        try:
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            logger.debug(f"[KimiClient] OK usage={data.get('usage', {})}")
            return data
        except requests.exceptions.HTTPError as e:
            logger.error(f"[KimiClient] HTTP {e.response.status_code}: {e.response.text[:500]}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"[KimiClient] Network error: {e}")
            raise

    def extract_reply(self, response_data: Dict[str, Any]) -> str:
        """Safely extract the assistant's text from a completion response."""
        try:
            return response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"[KimiClient] Malformed response: {e}")
            raise

    def extract_json(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and parse JSON from the assistant's reply."""
        text = self.extract_reply(response_data).strip()
        # Some models wrap JSON in markdown code fences
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"[KimiClient] JSON parse failed: {e} — text={text[:500]}")
            raise

    def health_check(self) -> bool:
        """Quick connectivity test."""
        if not self.api_key:
            return False
        try:
            self.chat_completion(
                messages=[{"role": "user", "content": "Say 'ok' only."}],
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.warning(f"[KimiClient] health_check failed: {e}")
            return False
