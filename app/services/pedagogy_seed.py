from __future__ import annotations

import json

from sqlalchemy.orm import Session

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

COMPETENCIES = ["speaking", "listening", "vocabulary", "grammar", "real-life communication", "confidence / fluency"]

UNITS_BY_LEVEL: dict[str, list[tuple[str, str, str]]] = {
    "A1": [
        ("Greetings and Introductions", "Handle greetings and introduce yourself in simple English.", "speaking"),
        ("Basic Questions", "Ask and answer simple daily questions.", "grammar"),
        ("Restaurant Basics", "Use core food vocabulary in a real scenario.", "real-life communication"),
        ("Simple Present", "Describe routines with correct simple present usage.", "grammar"),
    ],
    "A2": [
        ("Travel Basics", "Manage airport/hotel conversations.", "real-life communication"),
        ("Routine and Plans", "Talk about routine and future plans.", "speaking"),
        ("Past Basics", "Tell simple events in the past.", "grammar"),
        ("Asking for Help", "Request help politely in practical contexts.", "confidence / fluency"),
    ],
    "B1": [
        ("Expressing Opinions", "Share opinions with reasons.", "speaking"),
        ("Storytelling", "Tell coherent stories with transitions.", "fluency"),
        ("Meetings and Interviews", "Respond naturally in work interactions.", "real-life communication"),
        ("Negotiation Basics", "Use persuasive yet simple language.", "speaking"),
    ],
    "B2": [
        ("Professional Communication", "Communicate effectively at work with precision.", "real-life communication"),
        ("Persuasive Speaking", "Defend viewpoints with structure.", "speaking"),
        ("Presentations", "Deliver organized presentations confidently.", "confidence / fluency"),
        ("Nuanced Conversation", "Handle disagreement politely and clearly.", "grammar"),
    ],
    "C1": [
        ("Fluency Refinement", "Speak with high fluency and low hesitation.", "confidence / fluency"),
        ("Idiomatic Usage", "Apply idioms naturally in context.", "vocabulary"),
        ("Precision and Tone", "Adjust tone to formal and informal settings.", "real-life communication"),
        ("Advanced Argumentation", "Build and defend advanced arguments.", "speaking"),
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

VOCAB_SEED = [
    ("schedule", "agenda", "work", "B1", "workplace", "Can we check the schedule before the meeting?"),
    ("receipt", "recibo", "restaurant", "A2", "daily-life", "Can I get the receipt, please?"),
    ("deadline", "prazo", "work", "B2", "workplace", "We need to hit the project deadline."),
    ("negotiate", "negociar", "business", "B1", "workplace", "We need to negotiate better terms."),
    ("confident", "confiante", "general", "A2", "mindset", "I feel more confident speaking English."),
]


def ensure_pedagogical_seed(db: Session) -> None:
    if db.query(ProficiencyLevel.id).count() > 0:
        return

    for code, order_index, title in LEVELS:
        db.add(ProficiencyLevel(code=code, order_index=order_index, title=title, description=f"CEFR {code} level"))

    for level, _, _ in LEVELS:
        for competency in COMPETENCIES:
            slug = f"{level.lower()}-{competency.replace(' ', '-').replace('/', '')}"
            track = LearningTrack(
                slug=slug,
                title=f"{level} {competency.title()}",
                description=f"Adaptive track for {level} in {competency}",
                cefr_level=level,
            )
            db.add(track)
            db.flush()

            module = LearningModule(
                track_id=track.id,
                slug=f"module-{slug}",
                title=f"{level} Core {competency.title()}",
                description="Progressive competency module",
                competency=competency,
            )
            db.add(module)
            db.flush()

            for title, objective, primary_skill in UNITS_BY_LEVEL[level]:
                unit = LearningUnit(
                    module_id=module.id,
                    title=title,
                    description=f"{title} contextual practice",
                    cefr_level=level,
                    learning_objective=objective,
                    primary_skill=primary_skill,
                    secondary_skill="vocabulary" if primary_skill != "vocabulary" else "speaking",
                    prerequisites_json=json.dumps([]),
                    content_type="scenario",
                    is_pro_only=level in {"B2", "C1"},
                )
                db.add(unit)
                db.flush()
                db.add(LearningObjective(unit_id=unit.id, objective_text=objective))

    for topic in GRAMMAR_TOPICS:
        db.add(SkillTag(slug=topic.replace(" ", "-"), name=topic.title()))

    for term, translation, context, level, category, example in VOCAB_SEED:
        db.add(
            VocabularyItem(
                term=term,
                translation=translation,
                context=context,
                level=level,
                category=category,
                example=example,
                synonyms_json=json.dumps([]),
                frequency=1,
            )
        )

    db.commit()
