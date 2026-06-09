# test_auth.py - tests for /auth endpoints

import pytest
from httpx import AsyncClient


# ──────────────────────────────────────────────
# POST /auth/register
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "username": "user1",
        "email": "dup@example.com",
        "password": "password123"
    }
    await client.post("/auth/register", json=payload)

    # Try to register again with same email
    response = await client.post("/auth/register", json={
        "username": "user2",
        "email": "dup@example.com",
        "password": "password123"
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    await client.post("/auth/register", json={
        "username": "sameuser",
        "email": "first@example.com",
        "password": "password123"
    })
    response = await client.post("/auth/register", json={
        "username": "sameuser",
        "email": "second@example.com",
        "password": "password123"
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_password_too_short(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "short"
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "username": "newuser",
        "email": "not-an-email",
        "password": "password123"
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_username_too_short(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "username": "ab",
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 422


# ──────────────────────────────────────────────
# POST /auth/login
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, regular_user):
    response = await client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, regular_user):
    response = await client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient):
    response = await client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "password123"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_deactivated_user(client: AsyncClient, db_session, regular_user):
    # Deactivate user directly in DB
    regular_user.is_active = False
    db_session.add(regular_user)
    await db_session.commit()

    response = await client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    assert response.status_code == 403


# ──────────────────────────────────────────────
# POST /auth/logout
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, user_auth_headers, regular_user):
    # First login to get refresh token
    login_response = await client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]
    access_token = login_response.json()["access_token"]

    response = await client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


@pytest.mark.asyncio
async def test_logout_without_token(client: AsyncClient):
    response = await client.post(
        "/auth/logout",
        json={"refresh_token": "sometoken"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_access_after_logout_is_rejected(client: AsyncClient, regular_user, mock_redis):
    # Login
    login_response = await client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    # Logout
    await client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Try to access protected route with blacklisted token
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 401


# ──────────────────────────────────────────────
# POST /auth/refresh
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient, regular_user, mock_redis):
    login_response = await client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" not in data  # only access token is returned


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post("/auth/refresh", json={
        "refresh_token": "invalid.token.here"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_revoked_token(client: AsyncClient, regular_user, mock_redis):
    login_response = await client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    # Logout - revokes refresh token
    await client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Try to use revoked refresh token
    response = await client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 401