"""Test input validation schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest


class TestUserCreateValidation:
    """Test UserCreate schema validation."""

    def test_valid_user_data(self):
        """Test valid user data passes validation."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test123!@#",
            "full_name": "Test User",
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_invalid_email_format(self):
        """Test invalid email format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="invalid-email", username="testuser", password="Test123!@#"
            )
        assert "email" in str(exc_info.value).lower()

    def test_weak_password(self):
        """Test weak password raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", username="testuser", password="weak")
        assert "password" in str(exc_info.value).lower()

    def test_password_no_uppercase(self):
        """Test password without uppercase raises error."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com", username="testuser", password="test123!@#"
            )

    def test_password_no_lowercase(self):
        """Test password without lowercase raises error."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com", username="testuser", password="TEST123!@#"
            )

    def test_password_no_digit(self):
        """Test password without digit raises error."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com", username="testuser", password="TestTest!@#"
            )

    def test_password_no_special_char(self):
        """Test password without special character raises error."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com", username="testuser", password="TestTest123"
            )

    def test_username_too_short(self):
        """Test username too short raises error."""
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", username="ab", password="Test123!@#")

    def test_username_too_long(self):
        """Test username too long raises error."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com", username="a" * 31, password="Test123!@#"
            )

    def test_username_invalid_characters(self):
        """Test username with invalid characters raises error."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com", username="test@user", password="Test123!@#"
            )

    def test_reserved_username(self):
        """Test reserved username raises error."""
        reserved_names = ["admin", "administrator", "root", "system"]
        for name in reserved_names:
            with pytest.raises(ValidationError):
                UserCreate(
                    email="test@example.com", username=name, password="Test123!@#"
                )


class TestLoginRequestValidation:
    """Test LoginRequest schema validation."""

    def test_valid_login_data(self):
        """Test valid login data passes validation."""
        login_data = {"username": "testuser", "password": "Test123!@#"}
        login = LoginRequest(**login_data)
        assert login.username == "testuser"
        assert login.password == "Test123!@#"

    def test_missing_username(self):
        """Test missing username raises error."""
        with pytest.raises(ValidationError):
            LoginRequest(password="Test123!@#")

    def test_missing_password(self):
        """Test missing password raises error."""
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser")
