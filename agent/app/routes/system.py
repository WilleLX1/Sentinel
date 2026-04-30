from fastapi import APIRouter, Depends

from ..auth import require_api_key
from ..system_stats import system_overview

router = APIRouter(prefix="/api", tags=["system"], dependencies=[Depends(require_api_key)])


@router.get("/system")
async def system() -> dict:
    return system_overview()

