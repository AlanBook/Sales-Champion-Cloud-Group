from typing import Annotated

from fastapi import APIRouter, Depends

from sales_champion_backend.api.deps import DBSession, require_roles
from sales_champion_backend.db.models import User
from sales_champion_backend.schemas import SeedResponse
from sales_champion_backend.services.seed_service import load_demo_seed

router = APIRouter()


@router.post("/load", response_model=SeedResponse)
def load_seed(
    db: DBSession,
    _: Annotated[User, Depends(require_roles("admin", "boss"))],
) -> SeedResponse:
    load_demo_seed(db)
    return SeedResponse(ok=True, message="演示种子数据已加载。")
