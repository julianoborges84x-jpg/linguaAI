import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

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


def extract_output_text(data: dict) -> str:
    output = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    output.append(content.get("text", ""))
    return "".join(output).strip()


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

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{OPENAI_BASE_URL}/responses", json=body, headers=headers)
        if resp.status_code >= 400:
            raise HTTPException(status_code=500, detail=f"OpenAI error: {resp.text}")
        data = resp.json()

    return extract_output_text(data)


@app.post("/generate", response_model=GenerateOut)
def generate(payload: GenerateIn):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    output_text = call_openai(payload.instructions, payload.input)
    return GenerateOut(output=output_text)


@app.post("/detect-language", response_model=DetectOut)
def detect_language(payload: DetectIn):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    instructions = (
        "Detect the language of the input text and respond with the ISO 639-3 code only. "
        "Return exactly the code with no extra text."
    )
    output_text = call_openai(instructions, payload.input)
    code = output_text.strip().split()[0]
    return DetectOut(iso_code=code)
