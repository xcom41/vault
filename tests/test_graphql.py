STRONG = "TnsiasRu-i3o283GF4923h2kl3hi2ghh72783h2"


def _register(client, email="g@example.com"):
    r = client.post("/auth/register", json={"email": email, "password": STRONG})
    return r.json()["access_token"]


def _make_admin(db_session, email="g@example.com"):
    from app.models.user import User

    u = db_session.query(User).filter(User.email == email).first()
    u.is_admin = True
    db_session.commit()


def test_users_requires_admin(client, db_session):
    token = _register(client, "g@example.com")
    resp = client.post(
        "/graphql",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "{ users { id email } }"},
    )
    data = resp.json()
    assert data["errors"][0]["message"] == "Admin only"


def test_users_without_token(client):
    resp = client.post("/graphql", json={"query": "{ users { id email } }"})
    data = resp.json()
    assert data["errors"][0]["message"] == "Authentication required"


def test_admin_can_list_users(client, db_session):
    _register(client, "g@example.com")
    _make_admin(db_session, "g@example.com")
    login = client.post("/auth/login", json={"email": "g@example.com", "password": STRONG})
    token = login.json()["access_token"]
    resp = client.post(
        "/graphql",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "{ users { id email } }"},
    )
    assert "errors" not in resp.json()
    assert len(resp.json()["data"]["users"]) >= 1