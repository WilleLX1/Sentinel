from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .middleware import RateLimitMiddleware, RequestLogMiddleware
from .routes import actions, docker_routes, health, ping, system

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="Sentinel Agent",
    version="0.1.0",
    description="Read-only Docker and system monitoring agent for Sentinel.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Sentinel-Action-Key"],
)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)

app.include_router(ping.router)
app.include_router(system.router)
app.include_router(docker_routes.router)
app.include_router(health.router)
app.include_router(actions.router)


@app.get("/")
async def root() -> dict:
    return {"name": "sentinel-agent", "docs": "/docs"}

