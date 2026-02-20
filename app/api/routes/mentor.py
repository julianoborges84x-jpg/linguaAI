from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.ai import require_openai_api_key
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.history import LearningHistory
from app.models.language import Language
from app.models.user import PlanEnum, User
from app.schemas.mentor import MentorChatIn, MentorChatOut, MentorDetectIn, MentorDetectOut
from app.services.llm_client import detect_language, generate_reply

router = APIRouter(prefix="/mentor", tags=["mentor"])


def level_style(level: int) -> str:
    if level <= 3:
        return "Use frases curtas e vocabulario simples."
    if level <= 6:
        return "Use explicacoes moderadas com exemplos curtos."
    return "Use linguagem avancada, com nuances e termos tecnicos quando necessario."


def language_context(db: Session, code: str | None) -> Language | None:
    if not code:
        return None
    return db.query(Language).filter(Language.iso_code == code).first()


def build_instructions(user: User, target_language: Language | None, base_language: Language | None, feature: str) -> str:
    target_text = "Indefinido"
    if target_language:
        target_text = (
            f"{target_language.name} ({target_language.iso_code}), "
            f"regiao principal: {target_language.region}, familia: {target_language.family}"
        )
    base_text = "Indefinido"
    if base_language:
        base_text = (
            f"{base_language.name} ({base_language.iso_code}), "
            f"regiao principal: {base_language.region}, familia: {base_language.family}"
        )

    return (
        "Voce e o agente de IA MentorLingua."
        " Chame o aluno pelo nome em cada resposta."
        f" O nome do aluno e {user.name}."
        " Adapte a linguagem ao nivel do aluno."
        f" Nivel do aluno: {user.level}."
        f" {level_style(user.level)}"
        " Ensine escrita, conversacao, dialeto e vicios de linguagem conforme o pedido."
        " Corrija erros detalhadamente."
        " Explique diferencas culturais."
        " Explique diferencas formais e informais."
        f" O foco atual e: {feature}."
        f" Idioma alvo do aluno: {target_text}."
        f" Idioma base do aluno: {base_text}."
        " Ajuste o ensino conforme a estrutura gramatical do idioma alvo."
    )


def build_history_context(db: Session, user_id: int, limit: int = 10) -> str:
    items = (
        db.query(LearningHistory)
        .filter(LearningHistory.user_id == user_id)
        .order_by(LearningHistory.id.desc())
        .limit(limit)
        .all()
    )
    items.reverse()
    return "\n".join([f"{i.role}: {i.content}" for i in items])


@router.get("/history")
def get_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = (
        db.query(LearningHistory)
        .filter(LearningHistory.user_id == user.id)
        .order_by(LearningHistory.id.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "id": item.id,
            "feature": item.feature,
            "created_at": item.created_at.isoformat(),
            "preview": (item.content[:180] + "...") if len(item.content) > 180 else item.content,
        }
        for item in items
    ]


@router.get("/progress/weekly")
def weekly_progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        tz = ZoneInfo(user.timezone)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")

    today = datetime.now(tz).date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    results = []

    for day in days:
        start_local = datetime.combine(day, datetime.min.time(), tzinfo=tz)
        end_local = datetime.combine(day, datetime.max.time(), tzinfo=tz)
        start_utc = start_local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
        end_utc = end_local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

        count = (
            db.query(LearningHistory.id)
            .filter(
                LearningHistory.user_id == user.id,
                LearningHistory.created_at >= start_utc,
                LearningHistory.created_at <= end_utc,
            )
            .count()
        )
        results.append(
            {
                "date": day.isoformat(),
                "label": day.strftime("%a"),
                "count": count,
            }
        )

    return results


@router.post("/detect-language", response_model=MentorDetectOut)
def detect_base_language(
    payload: MentorDetectIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_openai_api_key()

    sample_text = payload.text.strip()
    if not sample_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text is required")

    iso_code = detect_language(sample_text)
    lang = db.query(Language).filter(Language.iso_code == iso_code).first()
    if not lang:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Detected language not supported")

    user.base_language_code = iso_code
    db.commit()
    return MentorDetectOut(iso_code=iso_code, name=lang.name)


@router.post("/chat", response_model=MentorChatOut)
def chat(
    payload: MentorChatIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_openai_api_key()

    if user.plan == PlanEnum.FREE and payload.feature != "writing":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Plan not allowed")

    target_language = language_context(db, user.target_language_code)
    base_language = language_context(db, user.base_language_code)

    if not target_language:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target language not set")

    history_text = build_history_context(db, user.id)
    instructions = build_instructions(user, target_language, base_language, payload.feature)
    input_text = payload.message
    if history_text:
        input_text = f"Historico:\n{history_text}\n\nMensagem atual:\n{payload.message}"

    reply = generate_reply(instructions, input_text)

    db.add(LearningHistory(user_id=user.id, role="user", content=payload.message, feature=payload.feature))
    db.add(LearningHistory(user_id=user.id, role="assistant", content=reply, feature=payload.feature))
    db.commit()

    ads = None
    if user.plan == PlanEnum.FREE:
        ads = ["Assine o plano PRO para desbloquear fala, dialeto e sem anuncios."]

    return MentorChatOut(reply=reply, ads=ads)
