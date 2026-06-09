# conftest.py - test fixtures

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from unittest.mock import AsyncMock, patch

from main import app
from database import Model, get_db
from models.users import UsersModel
from security import hash_password

# SQLite in-memory database URL for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)


# Override get_db dependency to use test SQLite database
async def override_get_db():
    async with test_session_maker() as session:
        yield session


# Create tables before all tests, drop after
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


# Clean all tables between tests
@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    yield
    async with test_session_maker() as session:
        for table in reversed(Model.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


# Mock Redis client - no real Redis needed for tests
@pytest.fixture(autouse=True)
def mock_redis():
    redis_store = {}  # in-memory dict simulates Redis

    async def mock_get(key):
        return redis_store.get(key)

    async def mock_setex(key, ttl, value):
        redis_store[key] = value

    async def mock_delete(key):
        redis_store.pop(key, None)

    with patch("dependencies.redis_client") as mock_client, \
         patch("services.auth_service.redis_client") as mock_service_client:

        for c in [mock_client, mock_service_client]:
            c.get = AsyncMock(side_effect=mock_get)
            c.setex = AsyncMock(side_effect=mock_setex)
            c.delete = AsyncMock(side_effect=mock_delete)

        yield redis_store


# HTTP client with overridden DB dependency
@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# DB session fixture for direct DB operations in tests
@pytest_asyncio.fixture
async def db_session():
    async with test_session_maker() as session:
        yield session


# Regular user fixture
@pytest_asyncio.fixture
async def regular_user(db_session: AsyncSession):
    user = UsersModel(
        email="user@example.com",
        username="testuser",
        hashed_password=hash_password("password123"),
        role="user",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# Admin user fixture
@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    user = UsersModel(
        email="admin@example.com",
        username="adminuser",
        hashed_password=hash_password("adminpass123"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# Auth headers fixture for regular user
@pytest_asyncio.fixture
async def user_auth_headers(client: AsyncClient, regular_user: UsersModel):
    response = await client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Auth headers fixture for admin user
@pytest_asyncio.fixture
async def admin_auth_headers(client: AsyncClient, admin_user: UsersModel):
    response = await client.post("/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}