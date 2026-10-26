STRONG = "Tr0ub4dor&3-Correct-Horse"


def test_register_login_me(client):
    r = client.post("/auth/register", json={"email": "u@example.com", "password": STRONG})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.post("/auth/login", json={"email": "u@example.com", "password": STRONG})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "u@example.com"


def test_weak_password_rejected(client):
    r = client.post("/auth/register", json={"email": "w@example.com", "password": "short"})
    assert r.status_code == 400


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "x@example.com", "password": STRONG})
    r = client.post("/auth/login", json={"email": "x@example.com", "password": "wrong-password-123"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid credentials"


def test_me_without_token(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_audit_login_success(client, db_session):
    from app.models.audit_event import AuditEvent

    client.post("/auth/register", json={"email": "a@example.com", "password": STRONG})
    client.post("/auth/login", json={"email": "a@example.com", "password": STRONG})
    events = db_session.query(AuditEvent).filter(AuditEvent.event_type == "user.login.success").all()
    assert len(events) >= 1