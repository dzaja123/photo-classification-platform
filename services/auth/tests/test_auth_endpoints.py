"""Test authentication endpoints."""

import pytest
from httpx import AsyncClient


class TestRegisterEndpoint:
    """Test user registration endpoint."""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, test_user_data):
        """Test successful user registration."""
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["email"] == test_user_data["email"]
        assert data["data"]["user"]["username"] == test_user_data["username"]
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient, test_user_data_invalid_email):
        """Test registration with invalid email."""
        response = await client.post("/api/v1/auth/register", json=test_user_data_invalid_email)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient, test_user_data_weak_password):
        """Test registration with weak password."""
        response = await client.post("/api/v1/auth/register", json=test_user_data_weak_password)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_reserved_username(self, client: AsyncClient, test_user_data_reserved_username):
        """Test registration with reserved username."""
        response = await client.post("/api/v1/auth/register", json=test_user_data_reserved_username)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user_data):
        """Test registration with duplicate email."""
        # First registration
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Second registration with same email
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "email" in data["detail"].lower() or "already" in data["detail"].lower()


class TestLoginEndpoint:
    """Test user login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data):
        """Test successful login."""
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_with_email(self, client: AsyncClient, test_user_data):
        """Test login with email instead of username."""
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login with email
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user_data):
        """Test login with wrong password."""
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login with wrong password
        login_data = {
            "username": test_user_data["username"],
            "password": "WrongPassword123!@#"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "Test123!@#"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401


class TestRefreshTokenEndpoint:
    """Test token refresh endpoint."""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, test_user_data):
        """Test successful token refresh."""
        # Register and get tokens
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        refresh_token = register_response.json()["data"]["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401


class TestGetMeEndpoint:
    """Test get current user endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_me_success(self, client: AsyncClient, test_user_data):
        """Test getting current user profile."""
        # Register and get access token
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        access_token = register_response.json()["data"]["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == test_user_data["email"]
        assert data["data"]["username"] == test_user_data["username"]
    
    @pytest.mark.asyncio
    async def test_get_me_unauthorized(self, client: AsyncClient):
        """Test getting current user without token."""
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 403  # No credentials
    
    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401


class TestLogoutEndpoint:
    """Test logout endpoint."""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, test_user_data):
        """Test successful logout."""
        # Register and get tokens
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        tokens = register_response.json()["data"]
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {access_token}"}
        logout_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/logout", json=logout_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
