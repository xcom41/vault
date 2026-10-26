from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from zxcvbn import zxcvbn

from app.config import settings


class WeakPasswordError(ValueError):
    pass


_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    return _hasher.hash(password + settings.password_pepper)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, password + settings.password_pepper)
    except VerifyMismatchError:
        return False


def validate_policy(password: str, user_inputs: list[str] | None = None) -> None:
    if len(password) < settings.password_min_length:
        raise WeakPasswordError(
            f"Password must be at least {settings.password_min_length} characters long"
        )
    result = zxcvbn(password, user_inputs=user_inputs or [])
    if result["score"] < 3:
        raise WeakPasswordError("Password is too weak")