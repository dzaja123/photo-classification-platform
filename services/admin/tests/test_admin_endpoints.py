"""Test admin endpoints."""

import pytest
from httpx import AsyncClient


class TestListSubmissionsEndpoint:
    """Test admin list submissions endpoint."""

    @pytest.mark.asyncio
    async def test_list_submissions_no_filters(self, client: AsyncClient):
        """Test listing submissions without filters."""
        response = await client.get("/api/v1/admin/submissions")

        assert response.status_code == 200
        data = response.json()
        assert "submissions" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

    @pytest.mark.asyncio
    async def test_list_submissions_age_filter(self, client: AsyncClient):
        """Test filtering by age range."""
        response = await client.get("/api/v1/admin/submissions?age_min=18&age_max=65")

        assert response.status_code == 200
        data = response.json()
        assert "submissions" in data

    @pytest.mark.asyncio
    async def test_list_submissions_gender_filter(self, client: AsyncClient):
        """Test filtering by gender."""
        response = await client.get("/api/v1/admin/submissions?gender=Male")

        assert response.status_code == 200
        data = response.json()
        assert "submissions" in data

    @pytest.mark.asyncio
    async def test_list_submissions_country_filter(self, client: AsyncClient):
        """Test filtering by country."""
        response = await client.get("/api/v1/admin/submissions?country=USA")

        assert response.status_code == 200
        data = response.json()
        assert "submissions" in data

    @pytest.mark.asyncio
    async def test_list_submissions_location_search(self, client: AsyncClient):
        """Test searching by location."""
        response = await client.get("/api/v1/admin/submissions?location=New York")

        assert response.status_code == 200
        data = response.json()
        assert "submissions" in data

    @pytest.mark.asyncio
    async def test_list_submissions_pagination(self, client: AsyncClient):
        """Test pagination parameters."""
        response = await client.get("/api/v1/admin/submissions?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_list_submissions_invalid_page(self, client: AsyncClient):
        """Test with invalid page number."""
        response = await client.get("/api/v1/admin/submissions?page=0")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_submissions_invalid_page_size(self, client: AsyncClient):
        """Test with invalid page size."""
        response = await client.get("/api/v1/admin/submissions?page_size=1000")

        assert response.status_code == 422  # Validation error (max 100)

    @pytest.mark.asyncio
    async def test_list_submissions_sorting(self, client: AsyncClient):
        """Test sorting parameters."""
        response = await client.get(
            "/api/v1/admin/submissions?sort_by=age&sort_order=asc"
        )

        assert response.status_code == 200
        data = response.json()
        assert "submissions" in data

    @pytest.mark.asyncio
    async def test_list_submissions_multiple_filters(self, client: AsyncClient):
        """Test combining multiple filters."""
        response = await client.get(
            "/api/v1/admin/submissions?age_min=18&age_max=65&gender=Male&country=USA"
        )

        assert response.status_code == 200
        data = response.json()
        assert "submissions" in data


class TestGetSubmissionEndpoint:
    """Test admin get single submission endpoint."""

    @pytest.mark.asyncio
    async def test_get_submission_not_found(self, client: AsyncClient):
        """Test getting non-existent submission."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/admin/submissions/{fake_uuid}")

        assert response.status_code == 404


class TestAnalyticsEndpoint:
    """Test analytics endpoint."""

    @pytest.mark.asyncio
    async def test_get_analytics(self, client: AsyncClient):
        """Test getting analytics data."""
        response = await client.get("/api/v1/admin/analytics")

        assert response.status_code == 200
        data = response.json()
        assert "total_submissions" in data
        assert "total_users" in data
        assert "submissions_today" in data
        assert "submissions_this_week" in data
        assert "submissions_this_month" in data
        assert "by_gender" in data
        assert "by_country" in data
        assert "by_classification" in data
        assert "by_status" in data
        assert "age_distribution" in data
        assert "avg_confidence" in data


class TestExportEndpoints:
    """Test export endpoints."""

    @pytest.mark.asyncio
    async def test_export_csv(self, client: AsyncClient):
        """Test CSV export."""
        response = await client.get("/api/v1/admin/export/submissions/csv")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]

    @pytest.mark.asyncio
    async def test_export_json(self, client: AsyncClient):
        """Test JSON export."""
        response = await client.get("/api/v1/admin/export/submissions/json")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert "attachment" in response.headers["content-disposition"]

    @pytest.mark.asyncio
    async def test_export_csv_with_filters(self, client: AsyncClient):
        """Test CSV export with filters."""
        response = await client.get(
            "/api/v1/admin/export/submissions/csv?age_min=18&gender=Male"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

    @pytest.mark.asyncio
    async def test_export_json_with_filters(self, client: AsyncClient):
        """Test JSON export with filters."""
        response = await client.get("/api/v1/admin/export/submissions/json?country=USA")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"


class TestAuditLogsEndpoint:
    """Test audit logs endpoint."""

    @pytest.mark.asyncio
    async def test_list_audit_logs(self, client: AsyncClient):
        """Test listing audit logs."""
        response = await client.get("/api/v1/admin/audit-logs")

        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert "page" in data

    @pytest.mark.asyncio
    async def test_list_audit_logs_with_event_type_filter(self, client: AsyncClient):
        """Test filtering audit logs by event type."""
        response = await client.get("/api/v1/admin/audit-logs?event_type=auth")

        assert response.status_code == 200
        data = response.json()
        assert "logs" in data

    @pytest.mark.asyncio
    async def test_list_audit_logs_with_user_filter(self, client: AsyncClient):
        """Test filtering audit logs by user."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/admin/audit-logs?user_id={fake_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert "logs" in data

    @pytest.mark.asyncio
    async def test_list_audit_logs_pagination(self, client: AsyncClient):
        """Test audit logs pagination."""
        response = await client.get("/api/v1/admin/audit-logs?page=1&page_size=20")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 20
