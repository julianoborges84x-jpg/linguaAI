from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.pedagogy import LearningModule, LearningTrack, LearningUnit, LearningUnitProgress, ReviewQueue
from app.models.user import User
from app.services.adaptive_learning_service import get_or_create_learner_profile, resolve_target_language_code

MODULE_BLUEPRINT = [
    (
        "primeiros-contatos",
        "Primeiros Contatos",
        [
            "Greetings and Introductions",
            "My Name Is...",
            "Countries and Languages",
            "Basic Classroom Phrases",
        ],
    ),
    (
        "vida-diaria",
        "Vida Diaria",
        [
            "Numbers and Age",
            "Days and Time",
            "Daily Routine",
            "Family Basics",
        ],
    ),
    (
        "pessoas-e-lugares",
        "Pessoas e Lugares",
        [
            "Describing People",
            "Places in the City",
            "There Is / There Are",
            "Directions Basics",
        ],
    ),
    (
        "comida-e-compras",
        "Comida e Compras",
        [
            "Food Vocabulary",
            "At the Restaurant",
            "Ordering Politely",
            "Prices and Quantities",
        ],
    ),
    (
        "trabalho-e-rotina",
        "Trabalho e Rotina",
        [
            "Jobs and Occupations",
            "Workday Basics",
            "Meetings and Introductions",
            "Simple Questions at Work",
        ],
    ),
    (
        "revisao-e-consolidacao",
        "Revisao e Consolidacao",
        [
            "Mixed Review 1",
            "Mixed Review 2",
            "Listening and Reading Consolidation",
            "Final Checkpoint A1 Start",
        ],
    ),
]


def _exercise_pack(title: str) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{title}-mc",
            "type": "multiple_choice",
            "prompt": "Choose the best option for the context.",
            "hint_pt": "Leia o contexto completo antes de escolher.",
        },
        {
            "id": f"{title}-fill",
            "type": "fill_in_the_blank",
            "prompt": "Complete the sentence with one word.",
            "hint_pt": "Pense na estrutura da frase, nao apenas no vocabulario.",
        },
        {
            "id": f"{title}-order",
            "type": "word_order",
            "prompt": "Order the words to build a correct sentence.",
            "hint_pt": "Lembre-se de sujeito + verbo + complemento.",
        },
        {
            "id": f"{title}-pt-en",
            "type": "translation_pt_en",
            "prompt": "Translate from Portuguese to English.",
            "hint_pt": "Priorize clareza e frases curtas.",
        },
        {
            "id": f"{title}-en-pt",
            "type": "translation_en_pt",
            "prompt": "Translate from English to Portuguese.",
            "hint_pt": "Cheque sentido, nao traducao literal.",
        },
        {
            "id": f"{title}-assoc",
            "type": "match_meaning",
            "prompt": "Match words and meanings.",
            "hint_pt": "Agrupe por contexto de uso.",
        },
        {
            "id": f"{title}-prod",
            "type": "short_production",
            "prompt": "Write one sentence about yourself using lesson vocabulary.",
            "hint_pt": "Use ao menos uma frase-chave da aula.",
        },
    ]


def _lesson_payload(unit: LearningUnit, module_name: str, order_index: int) -> dict[str, Any]:
    vocab = [f"{unit.title.split(' ')[0].lower()}", "hello", "please", "thank you", "I am"]
    key_phrases = [
        "Hi, my name is Ana.",
        "Nice to meet you.",
        "Can you help me, please?",
    ]
    return {
        "id": unit.id,
        "module_name": module_name,
        "order_index": order_index,
        "title": unit.title,
        "lesson_objective": unit.learning_objective,
        "cefr_level": unit.cefr_level,
        "estimated_duration_min": 12,
        "target_vocabulary": vocab,
        "key_structures": key_phrases,
        "grammar_explanation_pt": "Regra curta: use frases simples com ordem direta (sujeito + verbo + complemento).",
        "examples": [
            {"en": "I am from Brazil.", "pt": "Eu sou do Brasil."},
            {"en": "She is in the office.", "pt": "Ela esta no escritorio."},
            {"en": "Can I have water, please?", "pt": "Posso pedir agua, por favor?"},
        ],
        "exercises": _exercise_pack(unit.title),
        "ai_context": {
            "scenario": unit.title,
            "mentor_role": "supportive tutor",
            "mode": "guided_practice",
            "free_limit": 6,
        },
        "final_review": [
            "What did you learn in this lesson?",
            "Which phrase can you use today in real life?",
        ],
        "completion_criteria": {
            "min_exercises_correct": 4,
            "min_conversation_turns": 2,
            "checkpoint_required": True,
        },
    }


def _ordered_a1_units(db: Session, user: User) -> list[LearningUnit]:
    target_lang = resolve_target_language_code(user)
    return (
        db.query(LearningUnit)
        .join(LearningModule, LearningModule.id == LearningUnit.module_id)
        .join(LearningTrack, LearningTrack.id == LearningModule.track_id)
        .filter(
            LearningUnit.cefr_level == "A1",
            LearningTrack.target_language_code == target_lang,
        )
        .order_by(LearningUnit.id.asc())
        .limit(24)
        .all()
    )


def _get_or_create_progress(db: Session, user_id: int, unit_id: int) -> LearningUnitProgress:
    existing = (
        db.query(LearningUnitProgress)
        .filter(
            LearningUnitProgress.user_id == user_id,
            LearningUnitProgress.unit_id == unit_id,
        )
        .first()
    )
    if existing:
        return existing

    progress = LearningUnitProgress(
        user_id=user_id,
        unit_id=unit_id,
        current_step=0,
        total_steps=10,
        completed=False,
        score=0.0,
    )
    db.add(progress)

    try:
        db.flush()
        return progress
    except IntegrityError:
        db.rollback()
        existing_after_race = (
            db.query(LearningUnitProgress)
            .filter(
                LearningUnitProgress.user_id == user_id,
                LearningUnitProgress.unit_id == unit_id,
            )
            .first()
        )
        if existing_after_race:
            return existing_after_race
        raise


def _module_id_for_lesson(modules: list[dict[str, Any]], lesson_id: int | None) -> int | None:
    if lesson_id is None:
        return None
    for module in modules:
        for lesson in module.get("lessons", []):
            if int(lesson.get("id")) == int(lesson_id):
                return int(module["id"])
    return None


def get_current_track(db: Session, user: User) -> dict[str, Any]:
    profile = get_or_create_learner_profile(db, user.id)
    units = _ordered_a1_units(db, user)
    module_rows = get_modules(db, user)

    completed = 0
    current_lesson_id: int | None = None
    current_step_index = 0
    resume_available = False

    for unit in units:
        progress = _get_or_create_progress(db, user.id, unit.id)
        if progress.completed:
            completed += 1
            continue

        if progress.current_step > 0 and not resume_available:
            current_lesson_id = unit.id
            current_step_index = progress.current_step
            resume_available = True

    next_lesson_id: int | None = None
    for unit in units:
        progress = _get_or_create_progress(db, user.id, unit.id)
        if not progress.completed:
            next_lesson_id = unit.id
            break

    if current_lesson_id is None:
        current_lesson_id = next_lesson_id

    current_module_id = _module_id_for_lesson(module_rows, current_lesson_id)

    return {
        "track_slug": "english-foundations-a1",
        "track_title": "English Foundations A1",
        "estimated_level": profile.estimated_level,
        "entry_profile": "absolute beginner" if profile.estimated_level == "A1" else "beginner",
        "current_module_id": current_module_id,
        "current_lesson_id": current_lesson_id,
        "current_step_index": current_step_index,
        "resume_available": resume_available,
        "next_lesson_id": next_lesson_id,
        "completed_lessons": completed,
        "total_lessons": len(units),
    }


def get_modules(db: Session, user: User) -> list[dict[str, Any]]:
    units = _ordered_a1_units(db, user)
    grouped: list[dict[str, Any]] = []
    cursor = 0

    first_unfinished_seen = False

    for idx, (slug, name, lesson_titles) in enumerate(MODULE_BLUEPRINT, start=1):
        chunk = units[cursor : cursor + len(lesson_titles)]
        cursor += len(lesson_titles)

        done = 0
        lessons: list[dict[str, Any]] = []

        for unit in chunk:
            progress = _get_or_create_progress(db, user.id, unit.id)

            if progress.completed:
                done += 1
                status = "concluida"
            else:
                if not first_unfinished_seen:
                    status = "disponivel"
                    first_unfinished_seen = True
                else:
                    status = "bloqueada"

            lessons.append(
                {
                    "id": unit.id,
                    "title": unit.title,
                    "status": status,
                    "current_step": progress.current_step,
                    "total_steps": progress.total_steps,
                }
            )

        grouped.append(
            {
                "id": idx,
                "slug": slug,
                "title": name,
                "progress_percent": round((done / max(1, len(chunk))) * 100),
                "lessons": lessons,
            }
        )

    return grouped


def get_module_detail(db: Session, user: User, module_id: int) -> dict[str, Any] | None:
    modules = get_modules(db, user)
    for module in modules:
        if int(module["id"]) == int(module_id):
            return module
    return None


def get_lesson_detail(db: Session, user: User, lesson_id: int) -> dict[str, Any] | None:
    unit = db.query(LearningUnit).filter(LearningUnit.id == lesson_id).first()
    if not unit:
        return None

    module_name = "English Foundations A1"
    order_index = 1

    module_rows = get_modules(db, user)
    for module in module_rows:
        for index, lesson in enumerate(module["lessons"], start=1):
            if int(lesson["id"]) == int(lesson_id):
                module_name = module["title"]
                order_index = index
                break

    payload = _lesson_payload(unit, module_name, order_index)
    progress = _get_or_create_progress(db, user.id, lesson_id)

    payload["progress"] = {
        "current_step": progress.current_step,
        "total_steps": progress.total_steps,
        "completed": progress.completed,
        "score": round(progress.score, 2),
    }
    return payload


def submit_lesson(
    db: Session,
    user: User,
    lesson_id: int,
    correct_count: int,
    total_count: int,
    conversation_turns: int,
) -> dict[str, Any] | None:
    lesson = get_lesson_detail(db, user, lesson_id)
    if not lesson:
        return None

    progress = _get_or_create_progress(db, user.id, lesson_id)
    accuracy = (correct_count / max(1, total_count)) * 100.0

    progress.current_step = progress.total_steps
    progress.score = max(progress.score, min(100.0, accuracy))
    progress.completed = correct_count >= 4 and conversation_turns >= 2
    progress.updated_at = datetime.utcnow()
    db.add(progress)

    if not progress.completed:
        review = ReviewQueue(
            user_id=user.id,
            queue_type="lesson_recovery",
            reference_id=lesson_id,
            priority=4,
            due_at=datetime.utcnow() + timedelta(hours=6),
            status="pending",
        )
        db.add(review)
        next_review_at = review.due_at
    else:
        vocab_review = ReviewQueue(
            user_id=user.id,
            queue_type="lesson_vocab_review",
            reference_id=lesson_id,
            priority=2,
            due_at=datetime.utcnow() + timedelta(hours=18),
            status="pending",
        )
        phrase_review = ReviewQueue(
            user_id=user.id,
            queue_type="lesson_key_phrase_review",
            reference_id=lesson_id,
            priority=2,
            due_at=datetime.utcnow() + timedelta(days=1),
            status="pending",
        )
        db.add(vocab_review)
        db.add(phrase_review)
        next_review_at = vocab_review.due_at

    return {
        "lesson_id": lesson_id,
        "completed": progress.completed,
        "accuracy": round(accuracy, 1),
        "next_review_at": next_review_at.isoformat(),
        "next_step": "next_lesson" if progress.completed else "review_lesson",
    }


def save_lesson_step(db: Session, user: User, lesson_id: int, current_step: int) -> dict[str, Any] | None:
    lesson = get_lesson_detail(db, user, lesson_id)
    if not lesson:
        return None

    progress = _get_or_create_progress(db, user.id, lesson_id)
    bounded_step = max(0, min(current_step, progress.total_steps))
    progress.current_step = bounded_step
    progress.updated_at = datetime.utcnow()
    db.add(progress)

    return {
        "lesson_id": lesson_id,
        "current_step": progress.current_step,
        "total_steps": progress.total_steps,
        "completed": progress.completed,
        "score": round(progress.score, 2),
    }


def get_review_today(db: Session, user: User) -> dict[str, Any]:
    now = datetime.utcnow()
    items = (
        db.query(ReviewQueue)
        .filter(
            ReviewQueue.user_id == user.id,
            ReviewQueue.status == "pending",
            ReviewQueue.due_at <= now,
        )
        .order_by(ReviewQueue.priority.desc(), ReviewQueue.due_at.asc())
        .limit(30)
        .all()
    )

    payload = [
        {
            "id": item.id,
            "queue_type": item.queue_type,
            "reference_id": item.reference_id,
            "priority": item.priority,
            "due_at": item.due_at.isoformat(),
        }
        for item in items
    ]

    return {
        "items": payload,
        "estimated_minutes": max(5, len(payload) * 2),
    }


def submit_review_item(db: Session, user: User, review_item_id: int, correct: bool) -> dict[str, Any] | None:
    row = (
        db.query(ReviewQueue)
        .filter(
            ReviewQueue.id == review_item_id,
            ReviewQueue.user_id == user.id,
        )
        .first()
    )
    if not row:
        return None

    if correct:
        row.status = "done"
        next_due = datetime.utcnow() + timedelta(days=2)
    else:
        row.priority = min(5, row.priority + 1)
        row.due_at = datetime.utcnow() + timedelta(hours=8)
        next_due = row.due_at

    db.add(row)
    return {
        "review_item_id": review_item_id,
        "correct": correct,
        "next_review_at": next_due.isoformat(),
    }


def progress_summary(db: Session, user: User) -> dict[str, Any]:
    units = _ordered_a1_units(db, user)
    completed = 0
    mastered_vocab = 0

    for unit in units:
        progress = _get_or_create_progress(db, user.id, unit.id)
        if progress.completed:
            completed += 1

    due_review = (
        db.query(ReviewQueue)
        .filter(
            ReviewQueue.user_id == user.id,
            ReviewQueue.status == "pending",
            ReviewQueue.due_at <= datetime.utcnow(),
        )
        .count()
    )

    return {
        "lesson_progress": {"completed": completed, "total": len(units)},
        "module_completion": round((completed / max(1, len(units))) * 100),
        "vocabulary_mastered": mastered_vocab,
        "review_due": due_review,
        "estimated_level": get_or_create_learner_profile(db, user.id).estimated_level,
        "weekly_consistency": max(0, user.current_streak or 0),
    }