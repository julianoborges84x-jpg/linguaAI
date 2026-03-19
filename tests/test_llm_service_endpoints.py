from fastapi.testclient import TestClient

from llm_service import main as llm_main


def test_generate_returns_503_when_openai_key_missing(monkeypatch):
    monkeypatch.setattr(llm_main, "OPENAI_API_KEY", "")
    client = TestClient(llm_main.app)

    response = client.post("/generate", json={"instructions": "x", "input": "hello"})
    assert response.status_code == 503
    assert response.json()["detail"] == "OPENAI_API_KEY not configured"


def test_detect_language_returns_503_when_openai_key_missing(monkeypatch):
    monkeypatch.setattr(llm_main, "OPENAI_API_KEY", "")
    client = TestClient(llm_main.app)

    response = client.post("/detect-language", json={"input": "ola"})
    assert response.status_code == 503
    assert response.json()["detail"] == "OPENAI_API_KEY not configured"


def test_generate_returns_output(monkeypatch):
    monkeypatch.setattr(llm_main, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(llm_main, "call_openai", lambda instructions, input_text: "ok-response")
    client = TestClient(llm_main.app)

    response = client.post("/generate", json={"instructions": "x", "input": "hello"})
    assert response.status_code == 200
    assert response.json() == {"output": "ok-response"}


def test_generate_falls_back_on_quota_error(monkeypatch):
    monkeypatch.setattr(llm_main, "OPENAI_API_KEY", "test-key")

    def _raise_quota(*_args, **_kwargs):
        raise llm_main.OpenAIUpstreamError(429, "insufficient_quota")

    monkeypatch.setattr(llm_main, "call_openai", _raise_quota)
    client = TestClient(llm_main.app)

    response = client.post("/generate", json={"instructions": "x", "input": "I go yesterday"})
    assert response.status_code == 200
    assert "temporarily unavailable due to quota limits" in response.json()["output"]


def test_detect_language_falls_back_on_quota_error(monkeypatch):
    monkeypatch.setattr(llm_main, "OPENAI_API_KEY", "test-key")

    def _raise_quota(*_args, **_kwargs):
        raise llm_main.OpenAIUpstreamError(429, "insufficient_quota")

    monkeypatch.setattr(llm_main, "call_openai", _raise_quota)
    client = TestClient(llm_main.app)

    response = client.post("/detect-language", json={"input": "Ola, tudo bem?"})
    assert response.status_code == 200
    assert response.json() == {"iso_code": "por"}
