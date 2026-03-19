from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.immersion import (
    ImmersionDashboardOut,
    ImmersionFinishOut,
    ImmersionMissionOut,
    ImmersionScenarioOut,
    ImmersionStartIn,
    ImmersionStartOut,
    ImmersionTurnIn,
    ImmersionTurnOut,
    LandingPageOut,
    MissionClaimOut,
    MultiplayerChallengeIn,
    MultiplayerChallengeOut,
    NotificationSyncOut,
    RoleplayCharacterOut,
)
from app.services.immersion_service import (
    add_turn,
    build_immersion_dashboard,
    claim_mission,
    create_multiplayer_challenge,
    finish_immersion_session,
    join_multiplayer_challenge,
    landing_page_payload,
    list_characters_by_scenario,
    list_missions,
    list_scenarios,
    queue_smart_notifications,
    start_immersion_session,
)

router = APIRouter(prefix="/immersion", tags=["immersion"])


@router.get("/scenarios", response_model=list[ImmersionScenarioOut])
def scenarios(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = list_scenarios(db)
    return [
        ImmersionScenarioOut(
            id=row.id,
            slug=row.slug,
            title=row.title,
            category=row.category,
            difficulty=row.difficulty,
        )
        for row in rows
    ]


@router.get("/scenarios/{scenario_slug}/characters", response_model=list[RoleplayCharacterOut])
def characters(scenario_slug: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = list_characters_by_scenario(db, scenario_slug)
    return [
        RoleplayCharacterOut(
            id=row.id,
            name=row.name,
            personality=row.personality,
            accent=row.accent,
            objective=row.objective,
            difficulty=row.difficulty,
        )
        for row in rows
    ]


@router.post("/sessions/start", response_model=ImmersionStartOut)
def session_start(payload: ImmersionStartIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    session, character, opening = start_immersion_session(
        db,
        user,
        scenario_slug=payload.scenario_slug,
        character_id=payload.character_id,
        source=payload.source,
    )
    return ImmersionStartOut(
        session_id=session.id,
        scenario_slug=payload.scenario_slug,
        character=RoleplayCharacterOut(
            id=character.id,
            name=character.name,
            personality=character.personality,
            accent=character.accent,
            objective=character.objective,
            difficulty=character.difficulty,
        )
        if character
        else None,
        opening_message=opening,
    )


@router.post("/sessions/{session_id}/turn", response_model=ImmersionTurnOut)
def session_turn(
    session_id: int,
    payload: ImmersionTurnIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = add_turn(db, user, session_id, payload.message)
    return ImmersionTurnOut(**data)


@router.post("/sessions/{session_id}/finish", response_model=ImmersionFinishOut)
def session_finish(session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = finish_immersion_session(db, user, session_id)
    return ImmersionFinishOut(**data)


@router.get("/dashboard", response_model=ImmersionDashboardOut)
def immersion_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ImmersionDashboardOut(**build_immersion_dashboard(db, user))


@router.get("/missions", response_model=list[ImmersionMissionOut])
def missions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [ImmersionMissionOut(**item) for item in list_missions(db, user)]


@router.post("/missions/{mission_id}/claim", response_model=MissionClaimOut)
def missions_claim(mission_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return MissionClaimOut(**claim_mission(db, user, mission_id))


@router.post("/multiplayer/challenges", response_model=MultiplayerChallengeOut)
def multiplayer_create(
    payload: MultiplayerChallengeIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return MultiplayerChallengeOut(**create_multiplayer_challenge(db, user, payload.scenario_slug))


@router.post("/multiplayer/challenges/{challenge_id}/join", response_model=MultiplayerChallengeOut)
def multiplayer_join(challenge_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return MultiplayerChallengeOut(**join_multiplayer_challenge(db, user, challenge_id))


@router.post("/notifications/sync", response_model=NotificationSyncOut)
def notifications_sync(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return NotificationSyncOut(**queue_smart_notifications(db, user))


@router.get("/landing", response_model=LandingPageOut)
def landing():
    return LandingPageOut(**landing_page_payload())
