from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from sales_champion_backend.api.deps import DBSession, get_current_user
from sales_champion_backend.core.security import create_access_token, verify_password
from sales_champion_backend.db.models import User
from sales_champion_backend.schemas import LoginRequest, MeResponse, TokenResponse, UserSummary

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DBSession) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误。",
        )
    token = create_access_token(user.id, user.role_code)
    return TokenResponse(
        access_token=token,
        user=UserSummary(id=user.id, display_name=user.display_name, role_code=user.role_code),
    )


@router.get("/me", response_model=MeResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> MeResponse:
    return MeResponse(
        id=current_user.id,
        username=current_user.username,
        display_name=current_user.display_name,
        role_code=current_user.role_code,
        store_id=current_user.store_id,
    )
