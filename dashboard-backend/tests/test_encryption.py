from app.encryption import decrypt_text, encrypt_text


def test_encryption_roundtrip():
    encrypted = encrypt_text("secret-value")
    assert encrypted != "secret-value"
    assert decrypt_text(encrypted) == "secret-value"

