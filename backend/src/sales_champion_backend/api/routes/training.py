from typing import Annotated

from fastapi import APIRouter, Depends

from sales_champion_backend.api.deps import DBSession, get_current_user
from sales_champion_backend.db.models import User
from sales_champion_backend.schemas import TrainingEvaluateRequest, TrainingEvaluateResponse
from sales_champion_backend.services.training_service import evaluate_training

router = APIRouter()


@router.post("/evaluate", response_model=TrainingEvaluateResponse)
def evaluate_route(
    payload: TrainingEvaluateRequest,
    _: DBSession,
    __: Annotated[User, Depends(get_current_user)],
) -> TrainingEvaluateResponse:
    return evaluate_training(payload)
