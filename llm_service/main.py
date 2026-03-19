import os
import re
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure local runs pick up repo-level environment variables (same .env used by API).
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip().strip('"').strip("'")


OPENAI_API_KEY = _env("OPENAI_API_KEY")
OPENAI_MODEL = _env("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_BASE_URL = _env("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

app = FastAPI(title="LLM Service")


class GenerateIn(BaseModel):
    instructions: str
    input: str


class GenerateOut(BaseModel):
    output: str


class DetectIn(BaseModel):
    input: str


class DetectOut(BaseModel):
    iso_code: str


class OpenAIUpstreamError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def extract_output_text(data: dict) -> str:
    output = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    output.append(content.get("text", ""))
    return "".join(output).strip()


def fallback_generate(input_text: str) -> str:
    clean = input_text.strip()
    if not clean:
        return "I can help you practice English. Tell me one short sentence and I will improve it."
    return (
        "OpenAI is temporarily unavailable due to quota limits. "
        "Meanwhile, try this improved sentence in American English: "
        f"\"{clean}\""
    )


def fallback_detect_language(input_text: str) -> str:
    text = input_text.lower().strip()
    if re.search(r"\b(ola|você|voce|tudo bem|obrigado|bom dia|boa tarde)\b", text):
        return "por"
    if re.search(r"\b(hola|gracias|buenos dias|por favor|como estas)\b", text):
        return "spa"
    if re.search(r"\b(bonjour|merci|s'il vous plait|comment ca va)\b", text):
        return "fra"
    if re.search(r"\b(ciao|grazie|buongiorno|come stai)\b", text):
        return "ita"
    return "eng"


def call_openai(instructions: str, input_text: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENAI_MODEL,
        "instructions": instructions,
        "input": input_text,
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{OPENAI_BASE_URL}/responses", json=body, headers=headers)
            if resp.status_code >= 400:
                raise OpenAIUpstreamError(
                    status_code=resp.status_code,
                    detail=f"OpenAI error HTTP {resp.status_code}: {resp.text}",
                )
            data = resp.json()
    except httpx.TimeoutException as exc:
        raise OpenAIUpstreamError(status_code=504, detail="OpenAI timeout") from exc
    except httpx.HTTPError as exc:
        raise OpenAIUpstreamError(status_code=502, detail="OpenAI connection error") from exc

    return extract_output_text(data)


def generate_response(instructions: str, input_text: str) -> str:
    if not OPENAI_API_KEY:
        raise OpenAIUpstreamError(status_code=503, detail="OPENAI_API_KEY not configured")
    try:
        return call_openai(instructions, input_text)
    except OpenAIUpstreamError as exc:
        if exc.status_code == 429:
            return fallback_generate(input_text)
        raise


def detect_language_response(input_text: str) -> str:
    if not OPENAI_API_KEY:
        raise OpenAIUpstreamError(status_code=503, detail="OPENAI_API_KEY not configured")

    instructions = (
        "Detect the language of the input text and respond with the ISO 639-3 code only. "
        "Return exactly the code with no extra text."
    )
    try:
        output_text = call_openai(instructions, input_text)
        return output_text.strip().split()[0]
    except OpenAIUpstreamError as exc:
        if exc.status_code == 429:
            return fallback_detect_language(input_text)
        raise


@app.post("/generate", response_model=GenerateOut)
def generate(payload: GenerateIn):
    try:
        output_text = generate_response(payload.instructions, payload.input)
    except OpenAIUpstreamError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return GenerateOut(output=output_text)


@app.post("/detect-language", response_model=DetectOut)
def detect_language(payload: DetectIn):
    try:
        code = detect_language_response(payload.input)
    except OpenAIUpstreamError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return DetectOut(iso_code=code)
