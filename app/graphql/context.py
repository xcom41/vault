from ariadne import graphql_sync  # noqa: F401

from app.core.jwt import decode_token
from app.db.session import SessionLocal
from app.models.user import User


async def get_context_value(request, data=None):
    db = SessionLocal()
    user = None
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        try:
            payload = decode_token(auth.removeprefix("Bearer ").strip())
            user = db.query(User).filter(User.email == payload["sub"]).first()
            if user and not user.is_active:
                user = None
        except ValueError:
            user = None
    return {"request": request, "db": db, "user": user}