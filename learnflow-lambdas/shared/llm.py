"""Async LLM client for Mistral via Hugging Face Inference API."""

import httpx
import json
from .config import config


async def call_mistral(prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
    """
    Call Mistral LLM via Hugging Face Inference API.
    Returns the generated text response.
    """
    headers = {
        "Authorization": f"Bearer {config.HF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "return_full_text": False,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            config.HF_MODEL_ENDPOINT,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()

    result = response.json()

    # HF Inference API returns list of generated texts
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "")

    return ""


def parse_json_response(text: str) -> dict | list | None:
    """Attempt to extract JSON from LLM response text."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in response
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    # Try array
    start = text.find("[")
    end = text.rfind("]") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    return None
