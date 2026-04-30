from fastapi import APIRouter, Depends

from ..auth import require_api_key
from ..config import get_settings

router = APIRouter(prefix="/api", tags=["ping"], dependencies=[Depends(require_api_key)])


@router.get("/ping")
async def ping() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "agent": "sentinel-agent",
        "version": "0.1.0",
        "server_name": settings.server_name,
    }

