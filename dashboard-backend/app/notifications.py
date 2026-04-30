from __future__ import annotations

import json
import smtplib
from email.message import EmailMessage

import httpx
from sqlmodel import Session, select

from .config import get_settings
from .models import Alert, NotificationChannel


def _alert_text(alert: Alert) -> str:
    return f"[Sentinel] {alert.severity.upper()}: {alert.title}\n{alert.message}"


async def notify_alerts(session: Session, alerts: list[Alert]) -> None:
    for alert in alerts:
        await notify_alert(session, alert)


async def notify_alert(session: Session, alert: Alert) -> None:
    channels = session.exec(select(NotificationChannel).where(NotificationChannel.enabled == True)).all()  # noqa: E712
    settings = get_settings()

    if settings.discord_webhook_url:
        await _send_discord(settings.discord_webhook_url, _alert_text(alert))

    if settings.smtp_host and settings.smtp_from and settings.smtp_to:
        await _send_email(
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_username,
            settings.smtp_password,
            settings.smtp_from,
            settings.smtp_to,
            f"[Sentinel] {alert.title}",
            _alert_text(alert),
        )

    for channel in channels:
        config = json.loads(channel.config_json or "{}")
        if channel.type == "discord" and config.get("webhook_url"):
            await _send_discord(config["webhook_url"], _alert_text(alert))
        elif channel.type == "email":
            await _send_email(
                config.get("smtp_host") or settings.smtp_host,
                int(config.get("smtp_port") or settings.smtp_port),
                config.get("smtp_username") or settings.smtp_username,
                config.get("smtp_password") or settings.smtp_password,
                config.get("smtp_from") or settings.smtp_from,
                config.get("smtp_to") or settings.smtp_to,
                f"[Sentinel] {alert.title}",
                _alert_text(alert),
            )


async def _send_discord(webhook_url: str, content: str) -> None:
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.post(webhook_url, json={"content": content[:1900]})
        response.raise_for_status()


async def _send_email(
    host: str | None,
    port: int,
    username: str | None,
    password: str | None,
    sender: str | None,
    recipient: str | None,
    subject: str,
    body: str,
) -> None:
    if not host or not sender or not recipient:
        return
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    def send() -> None:
        with smtplib.SMTP(host, port, timeout=8) as smtp:
            smtp.starttls()
            if username and password:
                smtp.login(username, password)
            smtp.send_message(message)

    import asyncio

    await asyncio.to_thread(send)

async def send_test_notification(channel: NotificationChannel) -> dict:
    config = json.loads(channel.config_json or "{}")
    if channel.type == "discord":
        webhook_url = config.get("webhook_url") or get_settings().discord_webhook_url
        if not webhook_url:
            return {"status": "skipped", "message": "No Discord webhook configured"}
        await _send_discord(webhook_url, "[Sentinel] Test notification")
        return {"status": "sent", "message": "Discord notification sent"}
    if channel.type == "email":
        settings = get_settings()
        await _send_email(
            config.get("smtp_host") or settings.smtp_host,
            int(config.get("smtp_port") or settings.smtp_port),
            config.get("smtp_username") or settings.smtp_username,
            config.get("smtp_password") or settings.smtp_password,
            config.get("smtp_from") or settings.smtp_from,
            config.get("smtp_to") or settings.smtp_to,
            "[Sentinel] Test notification",
            "Sentinel email notification test.",
        )
        return {"status": "sent", "message": "Email notification attempted"}
    return {"status": "skipped", "message": "Unsupported notification channel type"}

