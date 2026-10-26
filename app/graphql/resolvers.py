from uuid import uuid4

from ariadne import MutationType, QueryType, convert_kwargs_to_snake_case
from graphql import GraphQLError

from app.audit.service import write_event
from app.core.jwt import create_access_token
from app.core.passwords import WeakPasswordError, hash_password, validate_policy
from app.models.audit_event import AuditEvent
from app.models.oauth_client import OAuthClient
from app.models.user import User

query = QueryType()
mutation = MutationType()


@query.field("me")
def resolve_me(_, info):
    return info.context["user"]


@query.field("users")
@convert_kwargs_to_snake_case
def resolve_users(_, info, search=None, limit=50, offset=0):
    db = info.context["db"]
    q = db.query(User)
    if search:
        q = q.filter(User.email.ilike(f"%{search}%"))
    return q.offset(offset).limit(limit).all()


@query.field("clients")
def resolve_clients(_, info):
    return info.context["db"].query(OAuthClient).all()


@query.field("auditEvents")
@convert_kwargs_to_snake_case
def resolve_audit_events(_, info, event_type=None, limit=50, offset=0):
    db = info.context["db"]
    q = db.query(AuditEvent)
    if event_type:
        q = q.filter(AuditEvent.event_type == event_type)
    return q.order_by(AuditEvent.created_at.desc()).offset(offset).limit(limit).all()


@mutation.field("registerUser")
def resolve_register_user(_, info, email, password):
    db = info.context["db"]
    if db.query(User).filter(User.email == email).first():
        raise GraphQLError("Email already registered")
    try:
        validate_policy(password, user_inputs=[email])
    except WeakPasswordError as exc:
        raise GraphQLError(str(exc))

    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    write_event(db, "user.created", actor_id=user.id, metadata={"email": user.email})
    return {"accessToken": create_access_token(user.email), "tokenType": "bearer"}


@mutation.field("createClient")
@convert_kwargs_to_snake_case
def resolve_create_client(_, info, name, is_confidential=True):
    db = info.context["db"]
    client = OAuthClient(
        client_id=str(uuid4()),
        name=name,
        is_confidential=is_confidential,
        redirect_uris=[],
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    write_event(db, "client.created", client_id=client.client_id, metadata={"name": name})
    return client


@mutation.field("disableUser")
@convert_kwargs_to_snake_case
def resolve_disable_user(_, info, user_id):
    db = info.context["db"]
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise GraphQLError("User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    write_event(db, "user.disabled", actor_id=user.id)
    return user