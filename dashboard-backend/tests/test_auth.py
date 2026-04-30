from app.auth import hash_password, verify_password


def test_password_hash_roundtrip():
    password_hash = hash_password("correct-horse")
    assert verify_password("correct-horse", password_hash)
    assert not verify_password("wrong", password_hash)

