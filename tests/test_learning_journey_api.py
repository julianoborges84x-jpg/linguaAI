from app.services.pedagogy_seed import ensure_pedagogical_seed
from app.services.learning_journey_service import _get_or_create_progress
from app.models.pedagogy import LearningUnitProgress
from sqlalchemy.exc import IntegrityError


def register_user(client, name, email, password):
    return client.post("/users", json={"name": name, "email": email, "password": password})


def login_user(client, email, password):
    return client.post("/auth/login", data={"username": email, "password": password})


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_learning_journey_endpoints(client, db_session):
    ensure_pedagogical_seed(db_session)
    register_user(client, "Journey", "journey@example.com", "secret123")
    token = login_user(client, "journey@example.com", "secret123").json()["access_token"]
    headers = auth_header(token)

    track = client.get("/pedagogy/track/current", headers=headers)
    assert track.status_code == 200
    assert track.json()["track_title"] == "English Foundations A1"

    modules = client.get("/pedagogy/modules", headers=headers)
    assert modules.status_code == 200
    assert len(modules.json()) >= 6

    first_module = modules.json()[0]
    module_detail = client.get(f"/pedagogy/modules/{first_module['id']}", headers=headers)
    assert module_detail.status_code == 200
    assert len(module_detail.json()["lessons"]) >= 4

    lesson_id = module_detail.json()["lessons"][0]["id"]
    lesson = client.get(f"/pedagogy/lessons/{lesson_id}", headers=headers)
    assert lesson.status_code == 200
    assert len(lesson.json()["exercises"]) >= 6

    submit = client.post(
        f"/pedagogy/lessons/{lesson_id}/submit",
        headers=headers,
        json={"correct_count": 5, "total_count": 6, "conversation_turns": 2},
    )
    assert submit.status_code == 200
    assert submit.json()["completed"] is True

    review_today = client.get("/pedagogy/review/today", headers=headers)
    assert review_today.status_code == 200
    assert "estimated_minutes" in review_today.json()

    if review_today.json()["items"]:
        review_id = review_today.json()["items"][0]["id"]
        review_submit = client.post("/pedagogy/review/submit", headers=headers, json={"review_item_id": review_id, "correct": True})
        assert review_submit.status_code == 200

    summary = client.get("/pedagogy/progress/summary", headers=headers)
    assert summary.status_code == 200
    assert "lesson_progress" in summary.json()


def test_lesson_step_persistence_and_resume(client, db_session):
    ensure_pedagogical_seed(db_session)
    register_user(client, "Resume", "resume@example.com", "secret123")
    token = login_user(client, "resume@example.com", "secret123").json()["access_token"]
    headers = auth_header(token)

    modules = client.get("/pedagogy/modules", headers=headers)
    assert modules.status_code == 200
    first_module = modules.json()[0]
    lesson_id = first_module["lessons"][0]["id"]

    save = client.post(f"/pedagogy/lessons/{lesson_id}/step", headers=headers, json={"current_step": 4})
    assert save.status_code == 200
    assert save.json()["current_step"] == 4

    track = client.get("/pedagogy/track/current", headers=headers)
    assert track.status_code == 200
    assert track.json()["current_lesson_id"] == lesson_id
    assert track.json()["current_step_index"] == 4
    assert track.json()["resume_available"] is True


def test_get_or_create_progress_returns_existing_without_duplicate(db_session):
    row = LearningUnitProgress(user_id=10, unit_id=20, current_step=2, total_steps=10, completed=False, score=0.0)
    db_session.add(row)
    db_session.commit()

    got = _get_or_create_progress(db_session, user_id=10, unit_id=20)
    assert got.id == row.id

    count = (
        db_session.query(LearningUnitProgress)
        .filter(LearningUnitProgress.user_id == 10, LearningUnitProgress.unit_id == 20)
        .count()
    )
    assert count == 1


def test_get_or_create_progress_recovers_from_integrity_error(db_session, monkeypatch):
    existing = LearningUnitProgress(user_id=30, unit_id=40, current_step=0, total_steps=10, completed=False, score=0.0)
    db_session.add(existing)
    db_session.commit()

    original_query = db_session.query

    class _MissingFirstQuery:
        def filter(self, *_args, **_kwargs):
            return self

        def first(self):
            return None

    lookup_calls = {"n": 0}

    def query_with_race(model, *args, **kwargs):
        if model is LearningUnitProgress:
            lookup_calls["n"] += 1
            if lookup_calls["n"] == 1:
                return _MissingFirstQuery()
        return original_query(model, *args, **kwargs)

    monkeypatch.setattr(db_session, "query", query_with_race)

    original_flush = db_session.flush
    calls = {"n": 0}

    def flush_with_integrity(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise IntegrityError("duplicate", params={}, orig=Exception("duplicate key"))
        return original_flush(*args, **kwargs)

    monkeypatch.setattr(db_session, "flush", flush_with_integrity)
    got = _get_or_create_progress(db_session, user_id=30, unit_id=40)
    assert got.id == existing.id
