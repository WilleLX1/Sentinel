from docker.errors import NotFound
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import require_action_key, require_api_key
from ..docker_client import DockerUnavailable, docker_service

router = APIRouter(
    prefix="/api/actions",
    tags=["actions"],
    dependencies=[Depends(require_api_key), Depends(require_action_key)],
)


class PullImageRequest(BaseModel):
    image: str


@router.post("/containers/{id_or_name}/{action}")
async def container_action(id_or_name: str, action: str) -> dict:
    if action not in {"restart", "start", "stop"}:
        raise HTTPException(status_code=400, detail="Unsupported action")
    try:
        return docker_service().container_action(id_or_name, action)
    except NotFound as exc:
        raise HTTPException(status_code=404, detail="Container not found") from exc
    except DockerUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"Docker unavailable: {exc}") from exc


@router.post("/images/pull")
async def pull_image(payload: PullImageRequest) -> dict:
    try:
        return docker_service().pull_image(payload.image)
    except DockerUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"Docker unavailable: {exc}") from exc

