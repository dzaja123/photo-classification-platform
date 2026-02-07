"""Pytest configuration and fixtures for application service tests."""

import asyncio
import os
import uuid
from io import BytesIO
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from PIL import Image

from app.main import app
from app.core.database import Base, get_db
from app.api.dependencies import get_current_user_id


# ---------------------------------------------------------------------------
# PostgreSQL test database (UUID columns require a real PG instance)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/photo_platform_test",
    ),
)

TEST_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

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


@pytest.fixture(autouse=True)
def _mock_storage():
    """Mock MinIO storage so tests don't need a live MinIO server."""
    mock_client = AsyncMock()
    with (
        patch(
            "app.services.submission_service.get_storage_client",
            return_value=mock_client,
        ),
        patch("app.api.v1.submissions.get_storage_client", return_value=mock_client),
    ):
        mock_client.upload_file.return_value = "photos/test/photo.jpg"
        mock_client.download_file.return_value = b"\xff\xd8\xff\xe0fake-jpeg-bytes"
        mock_client.delete_file.return_value = True
        yield mock_client


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with auth and DB overrides."""

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    async def override_get_current_user_id():
        return TEST_USER_ID

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_image_jpg():
    """Create a test JPEG image."""
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def test_image_png():
    """Create a test PNG image."""
    img = Image.new("RGB", (100, 100), color="blue")
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def test_submission_data():
    """Sample submission data for testing."""
    return {
        "name": "John Doe",
        "age": 30,
        "gender": "Male",
        "location": "New York",
        "country": "USA",
        "description": "Test photo submission",
    }


@pytest.fixture
def test_submission_data_invalid_age():
    """Invalid age test data."""
    return {
        "name": "John Doe",
        "age": 200,  # Invalid: > 150
        "gender": "Male",
        "location": "New York",
        "country": "USA",
    }
