from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

from app.config import settings


def create_access_token(sub: str, ttl_min: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    ttl = ttl_min if ttl_min is not None else settings.access_token_ttl_min
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl)).timestamp()),
        "jti": str(uuid4()),
        "typ": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc
    if payload.get("typ") != "access":
        raise ValueError("Invalid token type")
    return payload