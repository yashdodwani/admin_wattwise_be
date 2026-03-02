"""
Test script for WattWise Admin Portal API.

This script tests all authentication endpoints using pytest.

Usage:
    pytest tests/test_auth.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from models.admin import Base
from utils.dependencies import get_db

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestHealth:
    """Test health check endpoint."""

    def test_health_check(self):
        """Test GET /health."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAdminRegistration:
    """Test admin registration endpoint."""

    def test_register_admin_success(self):
        """Test successful admin registration."""
        response = client.post("/admin/register", json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "1234567890",
            "descom_name": "Power Company A",
            "is_active": True
        })
        assert response.status_code == 201
        data = response.json()
        assert data["admin_id"].startswith("ADM")
        assert len(data["admin_id"]) == 9  # ADM + 6 digits
        assert "generated_password" in data
        assert data["email"] == "john@example.com"

    def test_register_admin_duplicate_email(self):
        """Test registration with duplicate email."""
        # First registration
        client.post("/admin/register", json={
            "name": "John Doe",
            "email": "duplicate@example.com",
            "phone_number": "1234567890",
            "descom_name": "Power Company A"
        })

        # Second registration with same email
        response = client.post("/admin/register", json={
            "name": "Jane Doe",
            "email": "duplicate@example.com",
            "phone_number": "0987654321",
            "descom_name": "Power Company B"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_admin_invalid_email(self):
        """Test registration with invalid email."""
        response = client.post("/admin/register", json={
            "name": "John Doe",
            "email": "invalid-email",
            "phone_number": "1234567890",
            "descom_name": "Power Company A"
        })
        assert response.status_code == 422


class TestAdminLogin:
    """Test admin login endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data."""
        # Register admin for testing
        response = client.post("/admin/register", json={
            "name": "Login Tester",
            "email": "login@example.com",
            "phone_number": "1111111111",
            "descom_name": "Test Company"
        })
        self.admin_data = response.json()
        self.admin_id = self.admin_data["admin_id"]
        self.password = self.admin_data["generated_password"]

    def test_login_success(self):
        """Test successful login."""
        response = client.post("/admin/login", json={
            "admin_id": self.admin_id,
            "password": self.password
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600

    def test_login_invalid_admin_id(self):
        """Test login with invalid admin_id."""
        response = client.post("/admin/login", json={
            "admin_id": "ADM999999",
            "password": self.password
        })
        assert response.status_code == 401

    def test_login_invalid_password(self):
        """Test login with invalid password."""
        response = client.post("/admin/login", json={
            "admin_id": self.admin_id,
            "password": "WrongPassword123"
        })
        assert response.status_code == 401


class TestForgotPassword:
    """Test forgot password endpoint."""

    def test_forgot_password_success(self):
        """Test successful forgot password request."""
        # First register admin
        client.post("/admin/register", json={
            "name": "Forgot Test",
            "email": "forgot@example.com",
            "phone_number": "2222222222",
            "descom_name": "Test Company"
        })

        # Request password reset
        response = client.post("/admin/forgot-password", json={
            "email": "forgot@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert "OTP sent" in data["message"]
        assert data["expires_in"] == 600

    def test_forgot_password_nonexistent_email(self):
        """Test forgot password with non-existent email."""
        response = client.post("/admin/forgot-password", json={
            "email": "nonexistent@example.com"
        })
        assert response.status_code == 404


class TestProtectedRoute:
    """Test protected routes with authentication."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data."""
        # Register and login
        reg_response = client.post("/admin/register", json={
            "name": "Protected Tester",
            "email": "protected@example.com",
            "phone_number": "3333333333",
            "descom_name": "Test Company"
        })
        admin_data = reg_response.json()

        login_response = client.post("/admin/login", json={
            "admin_id": admin_data["admin_id"],
            "password": admin_data["generated_password"]
        })
        self.token = login_response.json()["access_token"]

    def test_get_profile_with_token(self):
        """Test getting profile with valid token."""
        response = client.get(
            "/admin/profile",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["admin_id"].startswith("ADM")
        assert data["email"] == "protected@example.com"

    def test_get_profile_without_token(self):
        """Test getting profile without token."""
        response = client.get("/admin/profile")
        assert response.status_code == 403

    def test_get_profile_with_invalid_token(self):
        """Test getting profile with invalid token."""
        response = client.get(
            "/admin/profile",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

