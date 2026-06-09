# test_users.py - tests for /users endpoints

import pytest
from httpx import AsyncClient


# ──────────────────────────────────────────────
# GET /users/me
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient, user_auth_headers, regular_user):
    response = await client.get("/users/me", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["username"] == "testuser"
    assert data["role"] == "user"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    response = await client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


# ──────────────────────────────────────────────
# GET /users/
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_all_users_as_admin(client: AsyncClient, admin_auth_headers, regular_user, admin_user):
    response = await client.get("/users/", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_all_users_as_regular_user(client: AsyncClient, user_auth_headers):
    response = await client.get("/users/", headers=user_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_all_users_no_token(client: AsyncClient):
    response = await client.get("/users/")
    assert response.status_code == 403


# ──────────────────────────────────────────────
# PATCH /users/me
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_username(client: AsyncClient, user_auth_headers, regular_user):
    response = await client.patch(
        "/users/me",
        json={"username": "newusername"},
        headers=user_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newusername"


@pytest.mark.asyncio
async def test_update_email(client: AsyncClient, user_auth_headers, regular_user):
    response = await client.patch(
        "/users/me",
        json={"email": "newemail@example.com"},
        headers=user_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newemail@example.com"


@pytest.mark.asyncio
async def test_update_both_fields(client: AsyncClient, user_auth_headers, regular_user):
    response = await client.patch(
        "/users/me",
        json={"username": "brandnew", "email": "brandnew@example.com"},
        headers=user_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "brandnew"
    assert data["email"] == "brandnew@example.com"


@pytest.mark.asyncio
async def test_update_no_fields(client: AsyncClient, user_auth_headers, regular_user):
    response = await client.patch(
        "/users/me",
        json={},
        headers=user_auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_duplicate_username(client: AsyncClient, user_auth_headers, regular_user, admin_user):
    # Try to take admin's username
    response = await client.patch(
        "/users/me",
        json={"username": "adminuser"},
        headers=user_auth_headers
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_duplicate_email(client: AsyncClient, user_auth_headers, regular_user, admin_user):
    response = await client.patch(
        "/users/me",
        json={"email": "admin@example.com"},
        headers=user_auth_headers
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_no_token(client: AsyncClient):
    response = await client.patch("/users/me", json={"username": "newname"})
    assert response.status_code == 403


# ──────────────────────────────────────────────
# DELETE /users/{user_id}
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_user_as_admin(client: AsyncClient, admin_auth_headers, regular_user):
    response = await client.delete(
        f"/users/{regular_user.id}",
        headers=admin_auth_headers
    )
    assert response.status_code == 200
    assert str(regular_user.id) in response.json()["message"]


@pytest.mark.asyncio
async def test_delete_user_as_regular_user(client: AsyncClient, user_auth_headers, admin_user):
    response = await client.delete(
        f"/users/{admin_user.id}",
        headers=user_auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_nonexistent_user(client: AsyncClient, admin_auth_headers):
    response = await client.delete(
        "/users/99999",
        headers=admin_auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_no_token(client: AsyncClient, regular_user):
    response = await client.delete(f"/users/{regular_user.id}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_deleted_user_cannot_login(client: AsyncClient, admin_auth_headers, regular_user):
    # Delete user
    await client.delete(f"/users/{regular_user.id}", headers=admin_auth_headers)

    # Try to login as deleted user
    response = await client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    assert response.status_code == 401