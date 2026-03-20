from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass

import httpx


@dataclass
class SmokeContext:
    base_url: str
    email: str
    password: str
    name: str


def _raise_for_status(response: httpx.Response, step: str) -> None:
    if response.status_code >= 400:
        detail = ""
        try:
            payload = response.json()
            detail = payload.get("detail") if isinstance(payload, dict) else str(payload)
        except Exception:
            detail = response.text[:500]
        raise RuntimeError(f"[{step}] {response.status_code} {response.request.method} {response.request.url} -> {detail}")


def _register(client: httpx.Client, ctx: SmokeContext) -> None:
    response = client.post(
        "/users",
        json={
            "name": ctx.name,
            "email": ctx.email,
            "password": ctx.password,
        },
    )
    if response.status_code not in (201, 409):
        _raise_for_status(response, "register")


def _login(client: httpx.Client, ctx: SmokeContext) -> str:
    response = client.post(
        "/auth/login",
        data={"username": ctx.email, "password": ctx.password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    _raise_for_status(response, "login")
    payload = response.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError("[login] access_token ausente")
    return str(token)


def _run() -> int:
    parser = argparse.ArgumentParser(description="Smoke test: login -> learning home -> module -> lesson -> submit -> refresh")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="API base URL")
    parser.add_argument("--email-prefix", default="smoke.learning", help="Email prefix used to create test user")
    parser.add_argument("--password", default="secret123", help="Password for smoke user")
    args = parser.parse_args()

    suffix = int(time.time())
    ctx = SmokeContext(
        base_url=args.base_url.rstrip("/"),
        email=f"{args.email_prefix}.{suffix}@example.com",
        password=args.password,
        name="Smoke Learning",
    )

    print(f"[smoke] base_url={ctx.base_url}")
    print(f"[smoke] user={ctx.email}")

    with httpx.Client(base_url=ctx.base_url, timeout=90.0, follow_redirects=True) as client:
        _register(client, ctx)
        token = _login(client, ctx)
        headers = {"Authorization": f"Bearer {token}"}

        onboarding = client.patch(
            "/users/me",
            headers=headers,
            json={"target_language": "en", "timezone": "America/Sao_Paulo"},
        )
        _raise_for_status(onboarding, "onboarding")

        track = client.get("/pedagogy/track/current", headers=headers)
        _raise_for_status(track, "track/current")
        track_payload = track.json()

        modules = client.get("/pedagogy/modules", headers=headers)
        _raise_for_status(modules, "modules")
        modules_payload = modules.json()
        if not modules_payload:
            raise RuntimeError("[modules] lista vazia")

        first_module_id = int(modules_payload[0]["id"])
        module_detail = client.get(f"/pedagogy/modules/{first_module_id}", headers=headers)
        _raise_for_status(module_detail, "modules/{id}")
        module_payload = module_detail.json()
        if not module_payload.get("lessons"):
            raise RuntimeError("[modules/{id}] sem aulas")

        first_lesson_id = int(module_payload["lessons"][0]["id"])
        lesson = client.get(f"/pedagogy/lessons/{first_lesson_id}", headers=headers)
        _raise_for_status(lesson, "lessons/{id}")
        lesson_payload = lesson.json()
        exercises = lesson_payload.get("exercises", [])
        if len(exercises) < 6:
            raise RuntimeError(f"[lessons/{first_lesson_id}] exercicios insuficientes: {len(exercises)}")

        for step in (1, 2, 3):
            save_step = client.post(
                f"/pedagogy/lessons/{first_lesson_id}/step",
                headers=headers,
                json={"current_step": step},
            )
            _raise_for_status(save_step, "lessons/{id}/step")
            if int(save_step.json().get("current_step", -1)) != step:
                raise RuntimeError(f"[lessons/{first_lesson_id}/step] etapa persistida inesperada")

        track_after_steps = client.get("/pedagogy/track/current", headers=headers)
        _raise_for_status(track_after_steps, "track/current after steps")
        track_after_payload = track_after_steps.json()
        if int(track_after_payload.get("current_lesson_id") or 0) != first_lesson_id:
            raise RuntimeError("[track/current] licao atual nao reflete retomada")
        if int(track_after_payload.get("current_step_index") or -1) != 3:
            raise RuntimeError("[track/current] etapa atual nao foi persistida")

        submit = client.post(
            f"/pedagogy/lessons/{first_lesson_id}/submit",
            headers=headers,
            json={"correct_count": 5, "total_count": 6, "conversation_turns": 2},
        )
        _raise_for_status(submit, "lessons/{id}/submit")

        review = client.get("/pedagogy/review/today", headers=headers)
        _raise_for_status(review, "review/today")
        recommendations = client.get("/pedagogy/recommendations", headers=headers)
        _raise_for_status(recommendations, "recommendations")
        summary = client.get("/pedagogy/progress/summary", headers=headers)
        _raise_for_status(summary, "progress/summary")

        output = {
            "track_title": track_payload.get("track_title"),
            "next_lesson_id": track_payload.get("next_lesson_id"),
            "module_count": len(modules_payload),
            "first_module_title": module_payload.get("title"),
            "first_lesson_title": lesson_payload.get("title"),
            "resumed_step_index": track_after_payload.get("current_step_index"),
            "exercise_count": len(exercises),
            "review_items_today": len(review.json().get("items", [])),
            "recommendation_count": len(recommendations.json()),
            "progress": summary.json().get("lesson_progress"),
        }
        print("[smoke] PASS")
        print(json.dumps(output, ensure_ascii=True, indent=2))
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(_run())
    except Exception as exc:
        print(f"[smoke] FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
