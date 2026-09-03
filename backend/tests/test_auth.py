"""Tests for authentication endpoints."""
from tests.conftest import client


def test_register_new_user():
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={"email": "newuser@krishix.com", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@krishix.com"


def test_register_duplicate_email():
    """Test registration with duplicate email."""
    # Create first user
    client.post(
        "/api/auth/register",
        json={"email": "duplicate@krishix.com", "password": "password123"}
    )
    
    # Try to register again
    response = client.post(
        "/api/auth/register",
        json={"email": "duplicate@krishix.com", "password": "password123"}
    )
    assert response.status_code == 409


def test_login_success():
    """Test successful login."""
    # Register user
    client.post(
        "/api/auth/register",
        json={"email": "login@krishix.com", "password": "password123"}
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "login@krishix.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@krishix.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_logout():
    """Test logout endpoint."""
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
