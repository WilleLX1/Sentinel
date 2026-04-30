from docker.errors import NotFound
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth import require_api_key
from ..docker_client import DockerUnavailable, docker_service

router = APIRouter(prefix="/api", tags=["docker"], dependencies=[Depends(require_api_key)])


def _service_unavailable(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Docker unavailable: {exc}")


@router.get("/docker")
async def docker_overview() -> dict:
    try:
        return docker_service().overview()
    except DockerUnavailable as exc:
        return {
            "docker_available": False,
            "error": str(exc),
            "containers_total": 0,
            "containers_running": 0,
            "containers_stopped": 0,
            "containers_unhealthy": 0,
            "images_total": 0,
            "volumes_total": 0,
            "networks_total": 0,
        }


@router.get("/docker/containers")
async def list_containers() -> list[dict]:
    try:
        return docker_service().list_containers()
    except DockerUnavailable as exc:
        raise _service_unavailable(exc) from exc


@router.get("/docker/containers/{id_or_name}")
async def container_detail(id_or_name: str) -> dict:
    try:
        return docker_service().get_container(id_or_name)
    except NotFound as exc:
        raise HTTPException(status_code=404, detail="Container not found") from exc
    except DockerUnavailable as exc:
        raise _service_unavailable(exc) from exc


@router.get("/docker/containers/{id_or_name}/logs")
async def container_logs(
    id_or_name: str,
    lines: int = Query(default=100, ge=1, le=2000),
    since: str | None = None,
    filter: str | None = None,
) -> dict:
    try:
        return docker_service().logs(id_or_name, lines=lines, since=since, filter_text=filter)
    except NotFound as exc:
        raise HTTPException(status_code=404, detail="Container not found") from exc
    except DockerUnavailable as exc:
        raise _service_unavailable(exc) from exc


@router.get("/docker/containers/{id_or_name}/stats")
async def container_stats(id_or_name: str) -> dict:
    try:
        return docker_service().stats(id_or_name)
    except NotFound as exc:
        raise HTTPException(status_code=404, detail="Container not found") from exc
    except DockerUnavailable as exc:
        raise _service_unavailable(exc) from exc


@router.get("/docker/images")
async def images() -> list[dict]:
    try:
        return docker_service().images()
    except DockerUnavailable as exc:
        raise _service_unavailable(exc) from exc


@router.get("/docker/networks")
async def networks() -> list[dict]:
    try:
        return docker_service().networks()
    except DockerUnavailable as exc:
        raise _service_unavailable(exc) from exc


@router.get("/docker/volumes")
async def volumes() -> list[dict]:
    try:
        return docker_service().volumes()
    except DockerUnavailable as exc:
        raise _service_unavailable(exc) from exc

