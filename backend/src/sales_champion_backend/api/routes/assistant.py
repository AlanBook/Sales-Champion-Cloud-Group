from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from sales_champion_backend.api.deps import DBSession, get_current_user
from sales_champion_backend.db.models import User
from sales_champion_backend.schemas import (
    AssistantRecommendRequest,
    AssistantRecommendResponse,
    ConversationMessageCreate,
    SessionResponse,
)
from sales_champion_backend.services.assistant_service import (
    append_message,
    create_session,
    get_session_detail,
    recommend,
)

router = APIRouter()


@router.post("/recommend", response_model=AssistantRecommendResponse)
def recommend_route(
    payload: AssistantRecommendRequest,
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> AssistantRecommendResponse:
    return recommend(db, payload)


@router.post("/session", response_model=SessionResponse)
def create_session_route(
    staff_id: str,
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> SessionResponse:
    session = create_session(db, staff_id)
    detail = get_session_detail(db, session.id)
    return SessionResponse(**detail)


@router.get("/session/{session_id}", response_model=SessionResponse)
def get_session_route(
    session_id: str,
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> SessionResponse:
    try:
        return SessionResponse(**get_session_detail(db, session_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/session/{session_id}/messages")
def append_message_route(
    session_id: str,
    payload: ConversationMessageCreate,
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> dict:
    try:
        message = append_message(db, session_id, payload.role, payload.content, payload.metadata)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "message_id": message.id}
