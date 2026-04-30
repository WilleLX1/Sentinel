from __future__ import annotations

SENSITIVE_KEYWORDS = (
    "PASSWORD",
    "PASS",
    "SECRET",
    "TOKEN",
    "API_KEY",
    "PRIVATE_KEY",
    "DATABASE_URL",
    "ACCESS_KEY",
    "AUTH",
    "SESSION",
    "COOKIE",
    "CREDENTIAL",
)


def is_sensitive_key(key: str) -> bool:
    upper = key.upper()
    return any(keyword in upper for keyword in SENSITIVE_KEYWORDS)


def redact_value(key: str, value: str | None) -> str | None:
    if value is None:
        return None
    if is_sensitive_key(key):
        return "[REDACTED]"
    return value


def redact_env(env: list[str] | dict[str, str] | None) -> dict[str, str]:
    if not env:
        return {}

    items: list[tuple[str, str]]
    if isinstance(env, dict):
        items = list(env.items())
    else:
        items = []
        for entry in env:
            key, _, value = entry.partition("=")
            if key:
                items.append((key, value))

    return {key: redact_value(key, value) or "" for key, value in items}

