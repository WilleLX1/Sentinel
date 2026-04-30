from __future__ import annotations

from typing import Any

import httpx

from .config import get_settings


class AgentClient:
    def __init__(self, base_url: str, api_key: str, action_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.action_key = action_key
        self.timeout = get_settings().agent_request_timeout_seconds

    def _headers(self, include_action_key: bool = False) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if include_action_key and self.action_key:
            headers["X-Sentinel-Action-Key"] = self.action_key
        return headers

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}", headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, json: dict[str, Any] | None = None, include_action_key: bool = False) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                headers=self._headers(include_action_key=include_action_key),
                json=json,
            )
            response.raise_for_status()
            return response.json()

