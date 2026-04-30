from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlmodel import Session, select

from ..auth import clear_session_cookie, get_current_user, set_session_cookie, verify_password
from ..database import get_session
from ..models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, response: Response, session: Session = Depends(get_session)) -> dict:
    user = session.exec(select(User).where(User.username == payload.username)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    set_session_cookie(response, user.username)
    return {"username": user.username, "is_admin": user.is_admin}


@router.post("/logout")
def logout(response: Response) -> dict:
    clear_session_cookie(response)
    return {"status": "ok"}


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict:
    return {"username": user.username, "is_admin": user.is_admin}

