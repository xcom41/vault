import pytest

from app.core.passwords import WeakPasswordError, hash_password, validate_policy, verify_password


def test_weak_password_rejected():
    with pytest.raises(WeakPasswordError):
        validate_policy("short", user_inputs=["user@example.com"])


def test_weak_pattern_rejected():
    with pytest.raises(WeakPasswordError):
        validate_policy("password1234", user_inputs=["user@example.com"])


def test_strong_password_accepted():
    validate_policy("Tr0ub4dor&3-Correct-Horse", user_inputs=["user@example.com"])


def test_hash_and_verify():
    h = hash_password("Tr0ub4dor&3-Correct-Horse")
    assert verify_password("Tr0ub4dor&3-Correct-Horse", h)
    assert not verify_password("wrong", h)