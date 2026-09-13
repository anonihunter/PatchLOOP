import json
import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()


class LLMError(Exception):
    pass

class LLM:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("LLM_MODEL", "gpt-4.1-mini")

    async def complete(self, system: str, user: str, json_mode: bool = False) -> str:
        if not self.api_key:
            raise LLMError("LLM_API_KEY is not configured")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.1,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            if r.status_code >= 400:
                raise LLMError(f"LLM HTTP {r.status_code}: {r.text[:1000]}")
            data = r.json()
            return data["choices"][0]["message"]["content"]

    async def json(self, system: str, user: str) -> dict:
        raw = await self.complete(system, user, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.S)
            if match:
                return json.loads(match.group(0))
            raise LLMError("LLM returned invalid JSON")
