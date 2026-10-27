import pytest

from app.core.passwords import WeakPasswordError, hash_password, validate_policy, verify_password


def test_weak_password_rejected():
    with pytest.raises(WeakPasswordError):
        validate_policy("short", user_inputs=["user@example.com"])


def test_weak_pattern_rejected():
    with pytest.raises(WeakPasswordError):
        validate_policy("password1234", user_inputs=["user@example.com"])


def test_strong_password_accepted():
    validate_policy("TnsiasRu-i3o283GF4923h2kl3hi2ghh72783h2", user_inputs=["user@example.com"])


def test_hash_and_verify():
    h = hash_password("TnsiasRu-i3o283GF4923h2kl3hi2ghh72783h2")
    assert verify_password("TnsiasRu-i3o283GF4923h2kl3hi2ghh72783h2", h)
    assert not verify_password("wrong", h)