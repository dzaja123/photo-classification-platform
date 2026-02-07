"""Pytest configuration and fixtures for admin service tests."""

import asyncio
import os
import uuid
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base, get_db
from app.core.mongodb import get_mongodb
from app.api.dependencies import get_current_admin


# ---------------------------------------------------------------------------
# PostgreSQL test database (UUID columns require a real PG instance)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@postgres:5432/photo_platform_test",
)

ADMIN_PAYLOAD = {
    "sub": str(uuid.UUID("22222222-2222-2222-2222-222222222222")),
    "username": "testadmin",
    "role": "ADMIN",
    "token_type": "access",
}

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
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


@pytest.fixture
def mock_mongodb():
    """Create a mock MongoDB database object."""
    mock_db = MagicMock()

    # Motor cursor: find() is sync, but to_list() is async
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    # Motor collection: find() is sync, count_documents() is async
    mock_collection = MagicMock()
    mock_collection.find.return_value = mock_cursor
    mock_collection.count_documents = AsyncMock(return_value=0)
    mock_collection.aggregate.return_value = mock_cursor

    # audit_logs.py accesses db.audit_logs (attribute), not db["audit_logs"]
    mock_db.audit_logs = mock_collection
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    return mock_db


@pytest.fixture
async def client(mock_mongodb) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with admin auth, DB, and MongoDB overrides."""

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    async def override_get_current_admin():
        return ADMIN_PAYLOAD

    async def override_get_mongodb():
        return mock_mongodb

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_admin] = override_get_current_admin
    app.dependency_overrides[get_mongodb] = override_get_mongodb

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
