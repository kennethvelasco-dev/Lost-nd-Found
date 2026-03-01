import sys
import json
from datetime import datetime, timezone
from backend import create_app
from backend.models.base import get_db_connection, init_db, DataBase
from backend.helpers.user_helpers import create_default_admin
import os

def log(msg):
    print(f"\n[PHASE 6.3 TEST] {msg}")

def run_phase_6_3_test():
    app = create_app()
    client = app.test_client()
    
    with app.app_context():
        # 1. Setup
        log("Setting up Database...")
        if os.path.exists(DataBase):
            os.remove(DataBase)
        init_db()
        create_default_admin() # Creates admin/AdminPass123!

        # 2. Register User
        log("Registering User...")
        user_data = {
            "username": "user63",
            "password": "Password123!",
            "name": "User 63",
            "email": "user63@test.com",
            "role": "user"
        }
        resp = client.post("/api/auth/register", json=user_data)
        if resp.status_code != 201:
            print(f"Registration failed: {resp.status_code} - {resp.get_json()}")
        assert resp.status_code == 201

        # 3. Login
        log("Logging in...")
        resp = client.post("/api/auth/login", json={"username": "user63", "password": "Password123!"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.get_json()}")
        user_token = resp.get_json()["data"]["token"] # Standardized
        user_headers = {"Authorization": f"Bearer {user_token}"}

        resp = client.post("/api/auth/login", json={"username": "admin", "password": "AdminPass123!"})
        admin_token = resp.get_json()["data"]["token"] # Standardized
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 4. Admin reports found item
        log("Admin reporting found item...")
        found_item = {
            "category": "Electronics",
            "item_type": "Smartphone",
            "brand": "Apple",
            "color": "Silver",
            "found_location": "Cafeteria",
            "found_datetime": "2026-03-01T12:00:00",
            "public_description": "Found an iPhone on a table."
        }
        resp = client.post("/api/items/found", json=found_item, headers=admin_headers)
        if resp.status_code != 201:
            print(f"Found item creation failed: {resp.get_json()}")
        found_item_id = resp.get_json()["data"]["item_id"] # Standardized
        log(f"Found item ID: {found_item_id}")

        # 5. User submits general report (no ID)
        log("User submitting general report (no ID)...")
        general_report = {
            "category": "Electronics",
            "item_type": "Smartphone",
            "brand": "Apple",
            "color": "Silver",
            "location": "Cafeteria",
            "datetime": "2026-03-01T11:45:00",
            "description": "Lost my silver iPhone at lunch."
        }
        resp = client.post("/api/claims/submit", json=general_report, headers=user_headers)
        if resp.status_code != 201:
            print(f"General report submission failed: {resp.get_json()}")
        assert resp.status_code == 201
        claim_id = resp.get_json()["data"]["claim_id"] # Standardized
        log(f"Claim ID: {claim_id}")

        # 6. Fetch potential matches
        log("Fetching potential matches...")
        resp = client.get(f"/api/claims/{claim_id}/potential-matches", headers=user_headers)
        matches = resp.get_json()["data"]["matches"] # Standardized
        assert len(matches) > 0
        best_match = matches[0]
        log(f"Best match score: {best_match['match_score']}")
        assert best_match["id"] == found_item_id
        assert best_match["match_score"] >= 90 

        # 7. Link claim
        log("Linking claim to item...")
        resp = client.post(f"/api/claims/{claim_id}/link", json={"found_item_id": found_item_id}, headers=user_headers)
        assert resp.status_code == 200

        # 8. Approve claim
        log("Approving claim...")
        resp = client.post(f"/api/claims/{claim_id}/verify", json={"decision": "approved"}, headers=admin_headers)
        assert resp.status_code == 200

        # 9. Schedule pickup
        log("Scheduling pickup...")
        schedule_data = {
            "pickup_datetime": "2026-03-10T15:00:00",
            "pickup_location": "Lost & Found Office, Room 101"
        }
        resp = client.post(f"/api/claims/{claim_id}/schedule", json=schedule_data, headers=admin_headers)
        assert resp.status_code == 200

        # 10. Verify final state
        log("Verifying final state...")
        resp = client.get("/api/claims/pending", headers=admin_headers)
        claims_data = resp.get_json()["data"] # Standardized
        my_claim = next(c for c in claims_data if c["claim_id"] == claim_id)
        assert my_claim["status"] == "approved"
        assert my_claim["pickup_datetime"] == "2026-03-10T15:00:00"
        
        log("PHASE 6.3 INTEGRATION TEST PASSED!")

if __name__ == "__main__":
    try:
        run_phase_6_3_test()
    except Exception as e:
        print(f"\n[FAIL] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
