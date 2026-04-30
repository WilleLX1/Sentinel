from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import socket
import ssl
import time

import httpx

from .models import HealthCheck


def _split_host_port(target: str, default_port: int) -> tuple[str, int]:
    if ":" in target:
        host, raw_port = target.rsplit(":", 1)
        return host, int(raw_port)
    return target, default_port


async def run_health_check(check: HealthCheck) -> dict:
    if check.type == "http":
        return await _http_check(check.target, check.expected_status or 200, check.timeout_seconds)
    if check.type == "tcp":
        host, port = _split_host_port(check.target, 80)
        return await _tcp_check(host, port, check.timeout_seconds)
    if check.type == "ssl":
        host, port = _split_host_port(check.target, 443)
        return await _ssl_check(host, port, check.timeout_seconds)
    return {"success": False, "status_code": None, "response_time_ms": 0, "message": f"Unsupported check type: {check.type}"}


async def _http_check(url: str, expected_status: int, timeout: int) -> dict:
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url)
        elapsed = int((time.perf_counter() - started) * 1000)
        return {
            "success": response.status_code == expected_status,
            "status_code": response.status_code,
            "response_time_ms": elapsed,
            "message": f"HTTP {response.status_code}",
        }
    except Exception as exc:
        return {"success": False, "status_code": None, "response_time_ms": int((time.perf_counter() - started) * 1000), "message": str(exc)}


async def _tcp_check(host: str, port: int, timeout: int) -> dict:
    started = time.perf_counter()
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return {"success": True, "status_code": None, "response_time_ms": int((time.perf_counter() - started) * 1000), "message": "Port is open"}
    except Exception as exc:
        return {"success": False, "status_code": None, "response_time_ms": int((time.perf_counter() - started) * 1000), "message": str(exc)}


def _ssl_probe(host: str, port: int, timeout: int) -> int:
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as wrapped:
            cert = wrapped.getpeercert()
    expires_raw = cert.get("notAfter")
    if not expires_raw:
        raise ValueError("Certificate expiry missing")
    expires_at = datetime.strptime(expires_raw, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    return (expires_at - datetime.now(timezone.utc)).days


async def _ssl_check(host: str, port: int, timeout: int) -> dict:
    started = time.perf_counter()
    try:
        days = await asyncio.to_thread(_ssl_probe, host, port, timeout)
        return {
            "success": days > 14,
            "status_code": None,
            "response_time_ms": int((time.perf_counter() - started) * 1000),
            "message": f"Certificate expires in {days} days",
        }
    except Exception as exc:
        return {"success": False, "status_code": None, "response_time_ms": int((time.perf_counter() - started) * 1000), "message": str(exc)}

