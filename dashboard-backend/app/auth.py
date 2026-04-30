from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
import secrets

from fastapi import Depends, HTTPException, Request, Response, status
from sqlmodel import Session, select

from .config import get_settings
from .database import get_session
from .models import User

HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 260_000
SESSION_COOKIE = "sentinel_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 12


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
    return "$".join(
        [
            HASH_ALGORITHM,
            str(HASH_ITERATIONS),
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        ]
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt_raw, digest_raw = password_hash.split("$", 3)
        if algorithm != HASH_ALGORITHM:
            return False
        iterations = int(iterations_raw)
        salt = base64.urlsafe_b64decode(salt_raw.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_raw.encode("ascii"))
    except Exception:
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return secrets.compare_digest(actual, expected)


def _sign(payload: str) -> str:
    secret = get_settings().dashboard_session_secret.encode("utf-8")
    return hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def create_session_token(username: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(seconds=SESSION_MAX_AGE_SECONDS)
    payload = base64.urlsafe_b64encode(
        json.dumps({"sub": username, "exp": int(expires.timestamp())}, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    return f"{payload}.{_sign(payload)}"


def parse_session_token(token: str | None) -> str | None:
    if not token or "." not in token:
        return None
    payload, signature = token.rsplit(".", 1)
    if not secrets.compare_digest(signature, _sign(payload)):
        return None
    try:
        data = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")).decode("utf-8"))
    except Exception:
        return None
    if int(data.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        return None
    return data.get("sub")


def set_session_cookie(response: Response, username: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(username),
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=False,
        samesite="lax",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE)


def get_current_user(request: Request, session: Session = Depends(get_session)) -> User:
    username = parse_session_token(request.cookies.get(SESSION_COOKIE))
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def ensure_admin_user(session: Session) -> None:
    settings = get_settings()
    existing = session.exec(select(User).where(User.username == settings.dashboard_admin_username)).first()
    password_hash = settings.dashboard_admin_password_hash or hash_password(settings.dashboard_admin_password)
    if existing:
        if settings.dashboard_admin_password_hash and existing.password_hash != settings.dashboard_admin_password_hash:
            existing.password_hash = settings.dashboard_admin_password_hash
            session.add(existing)
            session.commit()
        return
    session.add(User(username=settings.dashboard_admin_username, password_hash=password_hash, is_admin=True))
    session.commit()

