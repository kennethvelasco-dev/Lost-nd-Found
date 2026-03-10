import pytest
from backend.services.auth_service import register_user
from backend.models import ValidationError

def test_user_registration_success(app):
    user_data = {
        "username": "newuser",
        "password": "Password123!",
        "name": "New User",
        "email": "newuser@test.com",
        "role": "user"
    }
    with app.app_context():
        res, status = register_user(user_data)
        assert status == 201
        assert "access_token" in res

def test_admin_registration_success(app):
    admin_data = {
        "username": "newadmin",
        "password": "Password123!",
        "name": "New Admin",
        "email": "newadmin@test.com",
        "role": "admin",
        "admin_id": "ADM-002"
    }
    with app.app_context():
        res, status = register_user(admin_data)
        assert status == 201
        assert "access_token" in res

def test_admin_registration_missing_id(app):
    invalid_admin_data = {
        "username": "badadmin",
        "password": "Password123!",
        "name": "Bad Admin",
        "email": "badadmin@test.com",
        "role": "admin"
    }
    with app.app_context():
        with pytest.raises(ValidationError) as excinfo:
            register_user(invalid_admin_data)
        assert "Admin ID is required" in str(excinfo.value)

def test_registration_invalid_role(app):
    invalid_role_data = {
        "username": "invalidrole",
        "password": "Password123!",
        "name": "Invalid Role",
        "email": "invalid@test.com",
        "role": "superuser"
    }
    with app.app_context():
        with pytest.raises(ValidationError) as excinfo:
            register_user(invalid_role_data)
        assert "Role must be either 'user' or 'admin'" in str(excinfo.value)

def test_login_flow(client, app):
    # Register first
    user_data = {
        "username": "loginuser",
        "password": "Password123!",
        "name": "Login User",
        "email": "login@test.com",
        "role": "user"
    }
    with app.app_context():
        register_user(user_data)
    
    # Login
    response = client.post("/api/auth/login", json={
        "username": "loginuser",
        "password": "Password123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()["data"]
