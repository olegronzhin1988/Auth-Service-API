# Auth Service API

![Python](https://img.shields.io/badge/Python-3.13.9-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-8.6-DC382D?logo=redis&logoColor=white)
![Tests](https://img.shields.io/badge/tests-34%20passed-brightgreen?logo=pytest)
![CI](https://github.com/olegronzhin1988/Auth-Service-API/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A REST API for user authentication and authorization. Implements JWT access/refresh token flow with Redis-backed token storage, role-based access control, and full async stack. Built as a standalone auth service that can be integrated into any FastAPI project.

---

## Features

- User registration and login via email and password
- JWT access tokens (15 min) + refresh tokens (7 days)
- Refresh token storage in Redis with TTL-based auto-expiry
- Token blacklisting on logout — access tokens are invalidated immediately
- Role-based access control: `user` and `admin` roles
- Duplicate protection: unique email and username enforced at service level
- Fully async stack (asyncpg + SQLAlchemy async + redis-py async)
- Schema migrations via Alembic
- 34 tests on SQLite in-memory — no PostgreSQL or Redis needed for testing
- Continuous integration via GitHub Actions on every push and pull request

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 17 |
| Async DB driver | asyncpg |
| Token storage | Redis 8.6 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Password hashing | passlib + bcrypt |
| JWT | python-jose |
| Tests | pytest + pytest-asyncio + httpx |
| Containers | Docker Compose |
| CI | GitHub Actions |

---

## Project Structure

```
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI pipeline
├── main.py                    # FastAPI app entry point
├── config.py                  # Settings via pydantic-settings (.env)
├── database.py                # Engine, session, base ORM model
├── dependencies.py            # get_current_user, require_role, Redis client
├── security.py                # Password hashing, JWT encode/decode
├── alembic.ini                # Alembic configuration
├── compose.yaml                # Docker Compose: PostgreSQL + Redis
├── pytest.ini                 # pytest configuration
├── requirements.txt
├── .env.example                # Environment variable template
├── migrations/
│   ├── env.py
│   └── versions/
│       └── *_initial_migration.py
├── models/
│   └── users.py                # SQLAlchemy User model
├── schemas/
│   ├── users.py                # Pydantic user schemas
│   └── tokens.py               # Pydantic token schemas
├── routers/
│   ├── auth.py                 # /auth/* endpoints
│   └── users.py                # /users/* endpoints
├── services/
│   ├── auth_service.py          # Register, login, logout, refresh logic
│   └── users_service.py         # List, update, delete user logic
└── tests/
    ├── conftest.py              # Fixtures, SQLite override, Redis mock
    ├── test_auth.py             # 19 tests for /auth endpoints
    └── test_users.py            # 15 tests for /users endpoints
```

---

## Getting Started

### Prerequisites

- Python 3.13+
- Docker

### 1. Clone the repository

```bash
git clone https://github.com/olegronzhin1988/Auth-Service-API.git
cd Auth-Service-API
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Create the environment file

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env
```

`.env.example`:
```env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_db_name
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET_KEY=your_secret_key_min_32_chars
```

### 4. Start PostgreSQL and Redis via Docker Compose

```bash
docker compose up -d
```

### 5. Apply migrations

```bash
alembic upgrade head
```

### 6. Run the application

```bash
python main.py
```

API available at `http://127.0.0.1:8000`  
Interactive docs: `http://127.0.0.1:8000/docs`

---

## API

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Register a new user |
| `POST` | `/auth/login` | — | Login with email and password |
| `POST` | `/auth/logout` | Bearer token | Invalidate tokens |
| `POST` | `/auth/refresh` | — | Get a new access token via refresh token |

### Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/users/me` | Bearer token | Get current user profile |
| `GET` | `/users/` | Admin only | Get list of all users |
| `PATCH` | `/users/me` | Bearer token | Update username or email |
| `DELETE` | `/users/{user_id}` | Admin only | Delete user by ID |

---

## Request Examples

**Register:**
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "password": "securepass123"}'
```
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "securepass123"}'
```

**Access protected route:**
```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer eyJhbGci..."
```
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-06-09T12:00:00"
}
```

**Refresh access token:**
```bash
curl -X POST http://127.0.0.1:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGci..."}'
```

**Logout:**
```bash
curl -X POST http://127.0.0.1:8000/auth/logout \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGci..."}'
```

---

## Token Flow

```
POST /auth/login
        │
        ▼
  ┌─────────────┐     stored in Redis      ┌───────────────────────┐
  │ access_token│                           │ refresh:{user_id}     │
  │  (15 min)   │     refresh_token ───────►│ TTL: 7 days           │
  └──────┬──────┘                           └───────────────────────┘
         │
         │  sent in every request
         ▼
  Authorization: Bearer <access_token>
         │
         ▼
  get_current_user()
  ├── check blacklist in Redis
  ├── decode JWT → user_id
  └── fetch user from PostgreSQL


POST /auth/logout
  ├── add access_token to blacklist:{token} in Redis (TTL = remaining lifetime)
  └── delete refresh:{user_id} from Redis


POST /auth/refresh
  ├── decode refresh_token
  ├── verify token exists in Redis (not revoked)
  └── return new access_token
```

---

## Migrations

Tables are created **only via Alembic**, never at application startup.

```bash
# Apply all migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Generate a new migration after changing models
alembic revision --autogenerate -m "description"

# Show migration history
alembic history
```

---

## Tests

Tests use SQLite in-memory for the database and a mock dict for Redis — no real services needed.

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=. --cov-report=term-missing
```

**Coverage (34 tests):**

`test_auth.py` — registration (success, duplicate email/username, invalid input), login (success, wrong password, non-existent user, deactivated account), logout (success, no token, blacklist verification), token refresh (success, invalid token, revoked token).

`test_users.py` — get profile (success, no token, invalid token), list users (admin sees all, user gets 403), update profile (username, email, both fields, empty request, duplicate values), delete user (admin can, user cannot, non-existent ID, deleted user cannot login).

---

## Continuous Integration

Every push and pull request to `main` automatically triggers the test suite via GitHub Actions:

```
.github/workflows/ci.yml
```

The pipeline:
1. Checks out the code
2. Sets up Python 3.13.9
3. Installs dependencies from `requirements.txt`
4. Runs the full test suite with `pytest tests/ -v`

Required environment variables (PostgreSQL, Redis, JWT secret) are provided directly in the workflow — no `.env` file is needed in CI since tests run against SQLite in-memory and a mocked Redis client.

---

## Known Limitations / TODO

- [ ] OAuth2 social login (Google)
- [ ] Email verification on registration
- [ ] Password change endpoint
- [ ] Account deactivation endpoint
- [ ] Pagination for user list