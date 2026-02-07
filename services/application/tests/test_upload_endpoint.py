"""Test photo upload endpoint."""

import pytest
from httpx import AsyncClient
from io import BytesIO


class TestUploadEndpoint:
    """Test photo upload endpoint."""

    @pytest.mark.asyncio
    async def test_upload_success_jpg(
        self, client: AsyncClient, test_image_jpg, test_submission_data
    ):
        """Test successful photo upload with JPG."""
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        response = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_submission_data["name"]
        assert data["age"] == test_submission_data["age"]
        assert data["gender"] == test_submission_data["gender"]
        assert data["classification_status"] == "pending"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_upload_success_png(
        self, client: AsyncClient, test_image_png, test_submission_data
    ):
        """Test successful photo upload with PNG."""
        files = {"photo": ("test.png", test_image_png, "image/png")}
        response = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )

        assert response.status_code == 201
        data = response.json()
        assert data["classification_status"] == "pending"

    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(
        self, client: AsyncClient, test_submission_data
    ):
        """Test upload with invalid file type."""
        # Create a text file instead of image
        text_file = BytesIO(b"This is not an image")
        files = {"photo": ("test.txt", text_file, "text/plain")}
        response = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )

        assert response.status_code == 400
        assert "image" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_invalid_age(
        self, client: AsyncClient, test_image_jpg, test_submission_data_invalid_age
    ):
        """Test upload with invalid age."""
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        response = await client.post(
            "/api/v1/submissions/upload",
            data=test_submission_data_invalid_age,
            files=files,
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_upload_missing_required_field(
        self, client: AsyncClient, test_image_jpg
    ):
        """Test upload with missing required field."""
        incomplete_data = {
            "name": "John Doe",
            "age": 30,
            # Missing gender, location, country
        }
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        response = await client.post(
            "/api/v1/submissions/upload", data=incomplete_data, files=files
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_upload_missing_photo(
        self, client: AsyncClient, test_submission_data
    ):
        """Test upload without photo file."""
        response = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_upload_age_boundary_min(
        self, client: AsyncClient, test_image_jpg, test_submission_data
    ):
        """Test upload with minimum age (1)."""
        test_submission_data["age"] = 1
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        response = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_age_boundary_max(
        self, client: AsyncClient, test_image_jpg, test_submission_data
    ):
        """Test upload with maximum age (150)."""
        test_submission_data["age"] = 150
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        response = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_age_below_min(
        self, client: AsyncClient, test_image_jpg, test_submission_data
    ):
        """Test upload with age below minimum (0)."""
        test_submission_data["age"] = 0
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        response = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_upload_age_above_max(
        self, client: AsyncClient, test_image_jpg, test_submission_data
    ):
        """Test upload with age above maximum (151)."""
        test_submission_data["age"] = 151
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        response = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )

        assert response.status_code == 422  # Validation error


class TestListSubmissionsEndpoint:
    """Test list submissions endpoint."""

    @pytest.mark.asyncio
    async def test_list_submissions_empty(self, client: AsyncClient):
        """Test listing submissions when none exist."""
        response = await client.get("/api/v1/submissions/")

        assert response.status_code == 200
        data = response.json()
        assert data["submissions"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_submissions_pagination(self, client: AsyncClient):
        """Test pagination parameters."""
        response = await client.get("/api/v1/submissions/?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert "submissions" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    @pytest.mark.asyncio
    async def test_list_submissions_with_status_filter(
        self, client: AsyncClient, test_image_jpg, test_submission_data
    ):
        """Test listing submissions with status filter."""
        # Create a submission first
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )

        # Filter by pending status
        response = await client.get("/api/v1/submissions/?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Filter by completed status (should be empty)
        response = await client.get("/api/v1/submissions/?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestGetSubmissionEndpoint:
    """Test get single submission endpoint."""

    @pytest.mark.asyncio
    async def test_get_submission_not_found(self, client: AsyncClient):
        """Test getting non-existent submission."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/submissions/{fake_uuid}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_submission_success(
        self, client: AsyncClient, test_image_jpg, test_submission_data
    ):
        """Test getting an existing submission."""
        # Create a submission
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        create_resp = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )
        assert create_resp.status_code == 201
        submission_id = create_resp.json()["id"]

        # Get it
        response = await client.get(f"/api/v1/submissions/{submission_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == submission_id
        assert data["name"] == test_submission_data["name"]


class TestDeleteSubmissionEndpoint:
    """Test delete submission endpoint."""

    @pytest.mark.asyncio
    async def test_delete_submission_not_found(self, client: AsyncClient):
        """Test deleting non-existent submission."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/submissions/{fake_uuid}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_submission_success(
        self, client: AsyncClient, test_image_jpg, test_submission_data
    ):
        """Test successfully deleting a submission."""
        # Create a submission
        files = {"photo": ("test.jpg", test_image_jpg, "image/jpeg")}
        create_resp = await client.post(
            "/api/v1/submissions/upload", data=test_submission_data, files=files
        )
        assert create_resp.status_code == 201
        submission_id = create_resp.json()["id"]

        # Delete it
        response = await client.delete(f"/api/v1/submissions/{submission_id}")
        assert response.status_code == 204

        # Verify it's gone
        response = await client.get(f"/api/v1/submissions/{submission_id}")
        assert response.status_code == 404


class TestPhotoEndpoint:
    """Test photo retrieval endpoint."""

    @pytest.mark.asyncio
    async def test_get_photo_no_token(self, client: AsyncClient):
        """Test getting photo without token."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/submissions/{fake_uuid}/photo")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_photo_invalid_token(self, client: AsyncClient):
        """Test getting photo with invalid token."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(
            f"/api/v1/submissions/{fake_uuid}/photo?token=invalid-token"
        )
        assert response.status_code == 401
