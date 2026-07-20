async def test_register_success(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Alex",
            "last_name": "K",
            "nickname": "alexk",
            "email": "alex@example.com",
            "password": "secret123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alex@example.com"
    assert data["nickname"] == "alexk"
    assert "password" not in data
    assert "password_hash" not in data


async def test_register_duplicate_email(client, register_user):
    await register_user(email="dup@example.com", nickname="dupnick1")
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Other",
            "last_name": "User",
            "nickname": "dupnick2",
            "email": "dup@example.com",
            "password": "secret123",
        },
    )
    assert resp.status_code == 400


async def test_register_duplicate_nickname(client, register_user):
    await register_user(email="first@example.com", nickname="sharednick")
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Other",
            "last_name": "User",
            "nickname": "sharednick",
            "email": "second@example.com",
            "password": "secret123",
        },
    )
    assert resp.status_code == 400


async def test_login_success(client, register_user):
    await register_user(email="login@example.com", nickname="loginnick")
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "secret123", "remember_me": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client, register_user):
    await register_user(email="wrongpw@example.com", nickname="wrongpwnick")
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@example.com", "password": "not-the-password", "remember_me": False},
    )
    assert resp.status_code == 401


async def test_login_unknown_email(client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "secret123", "remember_me": False},
    )
    assert resp.status_code == 401


async def test_refresh_success(client, register_user, login_user):
    await register_user(email="refresh@example.com", nickname="refreshnick")
    tokens = await login_user(email="refresh@example.com")

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"]


async def test_refresh_invalid_token(client):
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert resp.status_code == 401


async def test_logout_invalidates_refresh_token(client, register_user, login_user):
    await register_user(email="logout@example.com", nickname="logoutnick")
    tokens = await login_user(email="logout@example.com")

    resp = await client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 204

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 401
