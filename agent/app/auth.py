from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .config import get_settings


def _extract_bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return authorization.split(" ", 1)[1].strip()


async def require_api_key(authorization: str | None = Header(default=None)) -> None:
    settings = get_settings()
    token = _extract_bearer(authorization)
    if not settings.sentinel_api_key or not secrets.compare_digest(token, settings.sentinel_api_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")


async def require_action_key(x_sentinel_action_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.sentinel_actions_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Remote actions are disabled")
    if not settings.sentinel_agent_admin_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action key is not configured")
    if not x_sentinel_action_key or not secrets.compare_digest(x_sentinel_action_key, settings.sentinel_agent_admin_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid action key")

