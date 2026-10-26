from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.audit.service import write_event
from app.auth.schemas import Credentials, MeResponse, TokenResponse
from app.core.deps import get_current_user
from app.core.jwt import create_access_token
from app.core.passwords import WeakPasswordError, hash_password, validate_policy, verify_password
from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(creds: Credentials, request: Request, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == creds.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        validate_policy(creds.password, user_inputs=[creds.email])
    except WeakPasswordError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    user = User(email=creds.email, hashed_password=hash_password(creds.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    write_event(
        db,
        "user.created",
        actor_id=user.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        metadata={"email": user.email},
    )
    return TokenResponse(access_token=create_access_token(user.email))


@router.post("/login", response_model=TokenResponse)
def login(creds: Credentials, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email).first()
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")

    if not user or not verify_password(creds.password, user.hashed_password):
        write_event(
            db,
            "user.login.failure",
            actor_id=user.id if user else None,
            ip=ip,
            user_agent=ua,
            metadata={"email": creds.email},
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    write_event(db, "user.login.success", actor_id=user.id, ip=ip, user_agent=ua)
    return TokenResponse(access_token=create_access_token(user.email))


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)):
    return MeResponse(id=user.id, email=user.email, is_admin=user.is_admin)