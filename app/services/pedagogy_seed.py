from __future__ import annotations

import json
from collections.abc import Iterable

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import ProgrammingError

from app.core.database import engine
from app.core.schema_compat import ensure_schema_compatibility
from app.models.pedagogy import (
    LearningModule,
    LearningObjective,
    LearningTrack,
    LearningUnit,
    ProficiencyLevel,
    SkillTag,
    VocabularyItem,
)

LEVELS = [
    ("A1", 1, "Beginner"),
    ("A2", 2, "Elementary"),
    ("B1", 3, "Intermediate"),
    ("B2", 4, "Upper Intermediate"),
    ("C1", 5, "Advanced"),
]

LANGUAGE_TARGETS = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
}

COMPETENCIES = [
    "speaking",
    "listening",
    "vocabulary",
    "grammar",
    "real-life communication",
    "confidence / fluency",
]

# Inspired by modern app-like progression (short practical units), without copying proprietary content.
UNITS_BY_LEVEL: dict[str, list[dict[str, str]]] = {
    "A1": [
        {"title": "Greetings", "objective": "Greet people and introduce yourself clearly.", "skill": "speaking"},
        {"title": "Basic Questions", "objective": "Ask and answer simple daily questions.", "skill": "grammar"},
        {"title": "Food Basics", "objective": "Order food and ask for prices politely.", "skill": "real-life communication"},
        {"title": "Simple Present", "objective": "Talk about routine using simple present.", "skill": "grammar"},
        {"title": "There Is / There Are", "objective": "Describe places and objects around you.", "skill": "grammar"},
        {"title": "Everyday Vocabulary", "objective": "Use high-frequency words for daily life.", "skill": "vocabulary"},
    ],
    "A2": [
        {"title": "Travel Basics", "objective": "Handle hotel, airport, and transport situations.", "skill": "real-life communication"},
        {"title": "Daily Routine", "objective": "Describe your day and habits naturally.", "skill": "speaking"},
        {"title": "Past Basics", "objective": "Describe what happened yesterday and last week.", "skill": "grammar"},
        {"title": "Shopping", "objective": "Buy items, compare options, and ask for help.", "skill": "real-life communication"},
        {"title": "Work Introductions", "objective": "Introduce your role and responsibilities.", "skill": "confidence / fluency"},
        {"title": "Future Plans", "objective": "Talk about plans using future forms.", "skill": "grammar"},
    ],
    "B1": [
        {"title": "Expressing Opinions", "objective": "Share opinions with reasons and examples.", "skill": "speaking"},
        {"title": "Storytelling", "objective": "Tell short stories with sequence and detail.", "skill": "confidence / fluency"},
        {"title": "Meetings", "objective": "Participate in meetings and clarify decisions.", "skill": "real-life communication"},
        {"title": "Interviews", "objective": "Answer common interview questions confidently.", "skill": "speaking"},
        {"title": "Problem Solving", "objective": "Discuss issues and propose practical solutions.", "skill": "real-life communication"},
        {"title": "Core Phrasal Verbs", "objective": "Use essential phrasal verbs in context.", "skill": "vocabulary"},
    ],
    "B2": [
        {"title": "Professional Communication", "objective": "Communicate precisely in professional contexts.", "skill": "real-life communication"},
        {"title": "Persuasive Speaking", "objective": "Defend ideas with structure and clarity.", "skill": "speaking"},
        {"title": "Nuanced Conversation", "objective": "Show nuance, contrast, and subtle meaning.", "skill": "confidence / fluency"},
        {"title": "Polite Disagreement", "objective": "Disagree politely and keep collaboration.", "skill": "real-life communication"},
        {"title": "Presentations", "objective": "Deliver concise and engaging presentations.", "skill": "speaking"},
        {"title": "Advanced Workplace", "objective": "Handle feedback, risk, and prioritization language.", "skill": "grammar"},
    ],
    "C1": [
        {"title": "Fluency Refinement", "objective": "Reduce hesitation and improve rhythm.", "skill": "confidence / fluency"},
        {"title": "Idiomatic Usage", "objective": "Use idioms and set phrases naturally.", "skill": "vocabulary"},
        {"title": "Precision and Tone", "objective": "Adjust tone for formal and informal goals.", "skill": "real-life communication"},
        {"title": "Advanced Professional Speaking", "objective": "Lead high-stakes discussions with confidence.", "skill": "speaking"},
        {"title": "Argumentation", "objective": "Build and defend complex arguments.", "skill": "grammar"},
        {"title": "Cultural Nuance", "objective": "Interpret and respond to cultural context.", "skill": "listening"},
    ],
}

GRAMMAR_TOPICS = [
    "simple present",
    "present continuous",
    "simple past",
    "future with going to / will",
    "question forms",
    "articles",
    "prepositions",
    "comparatives",
    "conditionals",
    "modal verbs",
    "workplace grammar",
    "conversation connectors",
]

VOCAB_SEED_BY_LANGUAGE = {
    "en": [
        ("schedule", "agenda", "work", "B1", "workplace", "Can we check the schedule before the meeting?"),
        ("receipt", "recibo", "restaurant", "A2", "daily-life", "Can I get the receipt, please?"),
        ("deadline", "prazo", "work", "B2", "workplace", "We need to hit the project deadline."),
        ("commute", "deslocamento", "daily", "A2", "routine", "My commute takes forty minutes."),
        ("negotiate", "negociar", "business", "B1", "workplace", "We need to negotiate better terms."),
    ],
    "es": [
        ("horario", "schedule", "work", "A2", "routine", "Cual es tu horario esta semana?"),
        ("recibo", "receipt", "restaurant", "A1", "daily-life", "Me da el recibo, por favor?"),
        ("plazo", "deadline", "work", "B1", "workplace", "Tenemos que cumplir el plazo final."),
        ("trayecto", "commute", "daily", "A2", "routine", "Mi trayecto al trabajo es corto."),
        ("negociar", "to negotiate", "business", "B1", "workplace", "Vamos a negociar el contrato."),
    ],
    "fr": [
        ("horaire", "schedule", "work", "A2", "routine", "Quel est ton horaire cette semaine?"),
        ("recu", "receipt", "restaurant", "A1", "daily-life", "Je peux avoir le recu, s'il vous plait?"),
        ("echeance", "deadline", "work", "B1", "workplace", "Nous devons respecter l'echeance."),
        ("trajet", "commute", "daily", "A2", "routine", "Mon trajet est assez rapide."),
        ("negocier", "to negotiate", "business", "B1", "workplace", "Il faut negocier de meilleures conditions."),
    ],
    "it": [
        ("orario", "schedule", "work", "A2", "routine", "Qual e il tuo orario questa settimana?"),
        ("scontrino", "receipt", "restaurant", "A1", "daily-life", "Posso avere lo scontrino, per favore?"),
        ("scadenza", "deadline", "work", "B1", "workplace", "Dobbiamo rispettare la scadenza."),
        ("tragitto", "commute", "daily", "A2", "routine", "Il mio tragitto e breve."),
        ("negoziare", "to negotiate", "business", "B1", "workplace", "Dobbiamo negoziare condizioni migliori."),
    ],
}


def _slugify(value: str) -> str:
    return value.strip().lower().replace(" ", "-").replace("/", "").replace("_", "-")


def _first_or_create(db: Session, model, filters: dict, payload: dict):
    row = db.query(model).filter_by(**filters).first()
    if row:
        return row
    row = model(**payload)
    db.add(row)
    db.flush()
    return row


def _seed_levels(db: Session) -> None:
    for code, order_index, title in LEVELS:
        _first_or_create(
            db,
            ProficiencyLevel,
            {"code": code},
            {
                "code": code,
                "order_index": order_index,
                "title": title,
                "description": f"CEFR {code} level",
            },
        )


def _seed_skill_tags(db: Session) -> None:
    for topic in GRAMMAR_TOPICS:
        slug = _slugify(topic)
        _first_or_create(
            db,
            SkillTag,
            {"slug": slug},
            {
                "slug": slug,
                "name": topic.title(),
            },
        )


def _seed_curriculum_for_language(db: Session, language_code: str, language_name: str) -> None:
    for level, _, _ in LEVELS:
        for competency in COMPETENCIES:
            track_slug = f"{language_code}-{level.lower()}-{_slugify(competency)}"
            track = _first_or_create(
                db,
                LearningTrack,
                {"slug": track_slug},
                {
                    "slug": track_slug,
                    "title": f"{language_name} {level} {competency.title()}",
                    "description": f"Adaptive {level} track for {language_name}: {competency}.",
                    "cefr_level": level,
                    "target_language_code": language_code,
                },
            )

            module_slug = f"module-{track_slug}"
            module = _first_or_create(
                db,
                LearningModule,
                {"slug": module_slug},
                {
                    "track_id": track.id,
                    "slug": module_slug,
                    "title": f"{language_name} {level} Core {competency.title()}",
                    "description": "Short practical lessons in a click-by-click progression.",
                    "competency": competency,
                },
            )

            for unit_seed in UNITS_BY_LEVEL[level]:
                title = f"{unit_seed['title']} ({language_name})"
                objective = f"{unit_seed['objective']} Target language: {language_name}."
                unit = _first_or_create(
                    db,
                    LearningUnit,
                    {"module_id": module.id, "title": title},
                    {
                        "module_id": module.id,
                        "title": title,
                        "description": f"{title} - interactive practice.",
                        "cefr_level": level,
                        "learning_objective": objective,
                        "primary_skill": unit_seed["skill"],
                        "secondary_skill": "vocabulary" if unit_seed["skill"] != "vocabulary" else "speaking",
                        "prerequisites_json": json.dumps([]),
                        "content_type": "click_lesson",
                        "is_pro_only": level in {"B2", "C1"},
                    },
                )

                _first_or_create(
                    db,
                    LearningObjective,
                    {"unit_id": unit.id, "objective_text": objective},
                    {
                        "unit_id": unit.id,
                        "objective_text": objective,
                    },
                )


def _seed_vocabulary(db: Session, language_code: str, rows: Iterable[tuple[str, str, str, str, str, str]]) -> None:
    for term, translation, context, level, category, example in rows:
        _first_or_create(
            db,
            VocabularyItem,
            {"term": term, "language_code": language_code, "level": level},
            {
                "term": term,
                "translation": translation,
                "context": context,
                "level": level,
                "category": category,
                "example": example,
                "synonyms_json": json.dumps([]),
                "frequency": 1,
                "language_code": language_code,
            },
        )


def ensure_pedagogical_seed(db: Session) -> None:
    try:
        seeded_track_langs = {
            row[0]
            for row in db.query(LearningTrack.target_language_code).distinct().all()
            if row and row[0]
        }
        total_units = db.query(func.count(LearningUnit.id)).scalar() or 0
        seeded_vocab_langs = {
            row[0]
            for row in db.query(VocabularyItem.language_code).distinct().all()
            if row and row[0]
        }
        if seeded_track_langs.issuperset(LANGUAGE_TARGETS.keys()) and total_units >= 96 and seeded_vocab_langs.issuperset(LANGUAGE_TARGETS.keys()):
            return
    except ProgrammingError:
        db.rollback()
        ensure_schema_compatibility(engine)

    _seed_levels(db)
    _seed_skill_tags(db)

    for lang_code, lang_name in LANGUAGE_TARGETS.items():
        _seed_curriculum_for_language(db, lang_code, lang_name)
        _seed_vocabulary(db, lang_code, VOCAB_SEED_BY_LANGUAGE[lang_code])

    db.commit()
