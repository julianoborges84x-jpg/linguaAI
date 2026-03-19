import os
import logging
import httpx
from app.core.config import settings

try:
    from llm_service.main import OpenAIUpstreamError, detect_language_response, generate_response
except Exception:  # pragma: no cover - optional import for externalized llm deployments
    OpenAIUpstreamError = None  # type: ignore[assignment]
    detect_language_response = None  # type: ignore[assignment]
    generate_response = None  # type: ignore[assignment]

logger = logging.getLogger("linguaai.llm_client")


def get_llm_service_url() -> str:
    return (settings.llm_service_url or os.getenv("LLM_SERVICE_URL", "http://localhost:8010")).rstrip("/")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


class LLMServiceError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _extract_output_text(data: dict) -> str:
    output = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    output.append(content.get("text", ""))
    return "".join(output).strip()


def _generate_with_openai_direct(instructions: str, input_text: str) -> str:
    api_key = (settings.openai_api_key or "").strip()
    if not api_key:
        raise LLMServiceError("OPENAI_API_KEY nao configurada e LLM_SERVICE_URL indisponivel.")

    headers = {
        "Authorization": f"Bearer {api_key}",
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
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException as exc:
        raise LLMServiceError("OpenAI demorou para responder. Tente novamente em instantes.") from exc
    except httpx.HTTPStatusError as exc:
        raise LLMServiceError(f"OpenAI retornou erro HTTP {exc.response.status_code}.") from exc
    except httpx.HTTPError as exc:
        raise LLMServiceError("Falha de comunicacao com OpenAI.") from exc

    return _extract_output_text(data)


def generate_reply(instructions: str, input_text: str) -> str:
    if generate_response is not None and OpenAIUpstreamError is not None:
        try:
            return generate_response(instructions, input_text)
        except OpenAIUpstreamError as exc:
            raise LLMServiceError(exc.detail) from exc

    logger.warning("Local llm_service import unavailable. Falling back to direct OpenAI call.")
    return _generate_with_openai_direct(instructions, input_text)


def detect_language(sample_text: str) -> str:
    if detect_language_response is not None and OpenAIUpstreamError is not None:
        try:
            return detect_language_response(sample_text)
        except OpenAIUpstreamError as exc:
            raise LLMServiceError(exc.detail) from exc

    logger.warning("Local llm_service import unavailable. Falling back to direct OpenAI language detection.")

    output = _generate_with_openai_direct(
        "Detect the language of the input and answer only with the ISO 639-3 code.",
        sample_text,
    )
    code = output.strip().split()[0] if output.strip() else ""
    if not code:
        raise LLMServiceError("Nao foi possivel detectar o idioma.")
    return code
