from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from sales_champion_backend.api.deps import DBSession, get_current_user
from sales_champion_backend.db.models import User
from sales_champion_backend.schemas import (
    ChampionDetailResponse,
    ChampionRankingResponse,
    DashboardOverviewResponse,
    ProductInsight,
    QuestionInsight,
    TeamWeakness,
)
from sales_champion_backend.services.analytics_service import (
    dashboard_overview,
    product_insights,
    team_weaknesses,
    top_objections,
    top_questions,
)
from sales_champion_backend.services.champion_service import get_ranking, get_staff_detail

router = APIRouter()


@router.get("/overview", response_model=DashboardOverviewResponse)
def overview(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> DashboardOverviewResponse:
    return DashboardOverviewResponse(**dashboard_overview(db))


@router.get("/champion-ranking", response_model=ChampionRankingResponse)
def ranking(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> ChampionRankingResponse:
    return ChampionRankingResponse(items=get_ranking(db))


@router.get("/champion/{staff_id}", response_model=ChampionDetailResponse)
def champion_detail(
    staff_id: str,
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> ChampionDetailResponse:
    try:
        return ChampionDetailResponse(**get_staff_detail(db, staff_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/questions", response_model=list[QuestionInsight])
def questions(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> list[QuestionInsight]:
    return [QuestionInsight(**item) for item in top_questions(db)]


@router.get("/objections", response_model=list[dict])
def objections(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> list[dict]:
    return top_objections(db)


@router.get("/product-insights", response_model=list[ProductInsight])
def products(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> list[ProductInsight]:
    return [ProductInsight(**item) for item in product_insights(db)]


@router.get("/team-weaknesses", response_model=list[TeamWeakness])
def weaknesses(
    db: DBSession,
    _: Annotated[User, Depends(get_current_user)],
) -> list[TeamWeakness]:
    return [TeamWeakness(**item) for item in team_weaknesses(db)]
