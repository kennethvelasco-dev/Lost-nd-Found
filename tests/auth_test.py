import json
from backend import create_app
from backend.models.base import init_db
from backend.services.auth_service import register_user
from backend.models import ValidationError

def test_auth_registration():
    app = create_app()
    with app.app_context():
        init_db()
        
        print("\n--- AUTH REGISTRATION TESTS ---")
        
        # 1. Valid User Registration
        print("Testing valid user registration...")
        user_data = {
            "username": "newuser",
            "password": "Password123!",
            "name": "New User",
            "email": "newuser@test.com",
            "role": "user"
        }
        res, status = register_user(user_data)
        assert status == 201
        assert "token" in res
        print("[PASS] Valid user registration")

        # 2. Valid Admin Registration (with admin_id)
        print("Testing valid admin registration...")
        admin_data = {
            "username": "newadmin",
            "password": "Password123!",
            "name": "New Admin",
            "email": "newadmin@test.com",
            "role": "admin",
            "admin_id": "ADM-002"
        }
        res, status = register_user(admin_data)
        assert status == 201
        assert "token" in res
        print("[PASS] Valid admin registration")

        # 3. Invalid Admin Registration (missing admin_id)
        print("Testing admin registration missing admin_id...")
        invalid_admin_data = {
            "username": "badadmin",
            "password": "Password123!",
            "name": "Bad Admin",
            "email": "badadmin@test.com",
            "role": "admin"
        }
        try:
            register_user(invalid_admin_data)
            print("[FAIL] Admin registration without admin_id should have failed")
        except ValidationError as ve:
            assert "Admin ID is required" in ve.message
            print(f"[PASS] Admin registration failed as expected: {ve.message}")

        # 4. Invalid Role Registration
        print("Testing registration with invalid role...")
        invalid_role_data = {
            "username": "invalidrole",
            "password": "Password123!",
            "name": "Invalid Role",
            "email": "invalid@test.com",
            "role": "superuser"
        }
        try:
            register_user(invalid_role_data)
            print("[FAIL] Registration with invalid role should have failed")
        except ValidationError as ve:
            assert "Role must be either 'user' or 'admin'" in ve.message
            print(f"[PASS] Invalid role registration failed as expected: {ve.message}")

        # 5. Missing Fields
        print("Testing registration with missing fields...")
        missing_fields_data = {
            "username": "missing",
            "password": "Password123!"
        }
        try:
            register_user(missing_fields_data)
            print("[FAIL] Registration with missing fields should have failed")
        except ValidationError as ve:
            assert "Missing required fields" in ve.message
            print(f"[PASS] Missing fields registration failed as expected: {ve.message}")

        print("\n✅ ALL AUTH REGISTRATION TESTS PASSED")

if __name__ == "__main__":
    test_auth_registration()
