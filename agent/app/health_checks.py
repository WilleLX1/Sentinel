from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import socket
import ssl
import time

import httpx


async def http_health_check(url: str, expected_status: int = 200, timeout: float = 5.0) -> dict:
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url)
        elapsed = int((time.perf_counter() - started) * 1000)
        return {
            "type": "http",
            "target": url,
            "success": response.status_code == expected_status,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "response_time_ms": elapsed,
            "message": f"HTTP {response.status_code}",
        }
    except Exception as exc:
        elapsed = int((time.perf_counter() - started) * 1000)
        return {
            "type": "http",
            "target": url,
            "success": False,
            "status_code": None,
            "expected_status": expected_status,
            "response_time_ms": elapsed,
            "message": str(exc),
        }


async def tcp_health_check(host: str, port: int, timeout: float = 5.0) -> dict:
    started = time.perf_counter()
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        elapsed = int((time.perf_counter() - started) * 1000)
        return {
            "type": "tcp",
            "target": f"{host}:{port}",
            "success": True,
            "response_time_ms": elapsed,
            "message": "Port is open",
        }
    except Exception as exc:
        elapsed = int((time.perf_counter() - started) * 1000)
        return {
            "type": "tcp",
            "target": f"{host}:{port}",
            "success": False,
            "response_time_ms": elapsed,
            "message": str(exc),
        }


def _ssl_probe(host: str, port: int, timeout: float) -> dict:
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as wrapped:
            cert = wrapped.getpeercert()
    expires_raw = cert.get("notAfter")
    if not expires_raw:
        raise ValueError("Certificate did not include an expiry date")
    expires_at = datetime.strptime(expires_raw, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    days_remaining = (expires_at - datetime.now(timezone.utc)).days
    return {
        "expires_at": expires_at.isoformat(),
        "days_remaining": days_remaining,
        "issuer": cert.get("issuer", []),
        "subject": cert.get("subject", []),
    }


async def ssl_health_check(host: str, port: int = 443, timeout: float = 5.0) -> dict:
    started = time.perf_counter()
    try:
        cert = await asyncio.to_thread(_ssl_probe, host, port, timeout)
        elapsed = int((time.perf_counter() - started) * 1000)
        return {
            "type": "ssl",
            "target": f"{host}:{port}",
            "success": cert["days_remaining"] > 14,
            "response_time_ms": elapsed,
            "message": f"Certificate expires in {cert['days_remaining']} days",
            **cert,
        }
    except Exception as exc:
        elapsed = int((time.perf_counter() - started) * 1000)
        return {
            "type": "ssl",
            "target": f"{host}:{port}",
            "success": False,
            "response_time_ms": elapsed,
            "message": str(exc),
        }

