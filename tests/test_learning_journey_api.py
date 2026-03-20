from app.services.pedagogy_seed import ensure_pedagogical_seed


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
