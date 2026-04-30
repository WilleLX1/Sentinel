from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet

from .config import get_settings


def _derive_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _fernet() -> Fernet:
    settings = get_settings()
    configured = settings.dashboard_encryption_key
    if configured:
        return Fernet(configured.encode("utf-8"))
    return Fernet(_derive_key(settings.dashboard_session_secret))


def encrypt_text(value: str | None) -> str:
    if not value:
        return ""
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(value: str | None) -> str:
    if not value:
        return ""
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")

