import os
import httpx

LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8010")


def generate_reply(instructions: str, input_text: str) -> str:
    payload = {
        "instructions": instructions,
        "input": input_text,
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(f"{LLM_SERVICE_URL}/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()
    return data.get("output", "")


def detect_language(sample_text: str) -> str:
    payload = {
        "input": sample_text,
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(f"{LLM_SERVICE_URL}/detect-language", json=payload)
        resp.raise_for_status()
        data = resp.json()
    return data.get("iso_code", "")
