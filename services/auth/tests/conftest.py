"""Pytest configuration and fixtures for auth service tests."""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db


# ---------------------------------------------------------------------------
# SQLite in-memory DB (StaticPool keeps a single shared connection)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def _setup_db():
    """Create and drop tables for every test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def _mock_redis():
    """Mock all Redis operations so tests don't need a live Redis server."""
    with (
        patch("app.middleware.rate_limit.increment_rate_limit", new_callable=AsyncMock, return_value=(True, 1)),
        patch("app.middleware.rate_limit.get_rate_limit_ttl", new_callable=AsyncMock, return_value=60),
        patch("app.api.dependencies.is_token_blacklisted", new_callable=AsyncMock, return_value=False),
        patch("app.core.cache.blacklist_token", new_callable=AsyncMock, return_value=True),
        patch("app.core.cache.is_token_blacklisted", new_callable=AsyncMock, return_value=False),
        patch("app.services.auth_service.blacklist_token", new_callable=AsyncMock, return_value=True),
        patch("app.services.auth_service.is_token_blacklisted", new_callable=AsyncMock, return_value=False),
    ):
        yield


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with DB override."""
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!@#",
        "full_name": "Test User"
    }


@pytest.fixture
def test_user_data_invalid_email():
    """Invalid email test data."""
    return {
        "email": "invalid-email",
        "username": "testuser",
        "password": "Test123!@#",
        "full_name": "Test User"
    }


@pytest.fixture
def test_user_data_weak_password():
    """Weak password test data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "weak",
        "full_name": "Test User"
    }


@pytest.fixture
def test_user_data_reserved_username():
    """Reserved username test data."""
    return {
        "email": "test@example.com",
        "username": "admin",
        "password": "Test123!@#",
        "full_name": "Test User"
    }
