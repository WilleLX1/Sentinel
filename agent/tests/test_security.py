from app.security import is_sensitive_key, redact_env


def test_sensitive_key_detection():
    assert is_sensitive_key("DATABASE_URL")
    assert is_sensitive_key("my_secret_token")
    assert not is_sensitive_key("PUBLIC_HOST")


def test_redact_env_from_docker_list():
    env = redact_env(["DATABASE_URL=postgres://user:pass@host/db", "PORT=8000", "API_KEY=abc"])
    assert env["DATABASE_URL"] == "[REDACTED]"
    assert env["API_KEY"] == "[REDACTED]"
    assert env["PORT"] == "8000"

