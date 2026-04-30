from fastapi import APIRouter, Depends, Query

from ..auth import require_api_key
from ..health_checks import http_health_check, ssl_health_check, tcp_health_check

router = APIRouter(prefix="/api/health", tags=["health"], dependencies=[Depends(require_api_key)])


@router.get("/http")
async def http_check(
    url: str,
    expected_status: int = Query(default=200, ge=100, le=599),
    timeout: float = Query(default=5.0, gt=0, le=30),
) -> dict:
    return await http_health_check(url, expected_status=expected_status, timeout=timeout)


@router.get("/tcp")
async def tcp_check(host: str, port: int = Query(ge=1, le=65535), timeout: float = Query(default=5.0, gt=0, le=30)) -> dict:
    return await tcp_health_check(host, port, timeout=timeout)


@router.get("/ssl")
async def ssl_check(host: str, port: int = Query(default=443, ge=1, le=65535), timeout: float = Query(default=5.0, gt=0, le=30)) -> dict:
    return await ssl_health_check(host, port=port, timeout=timeout)

