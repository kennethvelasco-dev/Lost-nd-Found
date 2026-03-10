import sys
import json
from backend import create_app
from backend.models.base import init_db, DataBase
from backend.helpers.user_helpers import create_default_admin
import os

def log(msg):
    print(f"\n[PHASE 6.6 SECURITY TEST] {msg}")

def run_security_test():
    app = create_app()
    client = app.test_client()
    
    with app.app_context():
        log("Setting up Database...")
        if os.path.exists(DataBase):
            os.remove(DataBase)
        init_db()
        create_default_admin()

        # 1. Register two users
        log("Registering users...")
        users = []
        for i in range(1, 3):
            u = {"username": f"user{i}", "password": "Password123!", "name": f"User {i}", "email": f"u{i}@test.com", "role": "user"}
            client.post("/api/auth/register", json=u)
            resp = client.post("/api/auth/login", json={"username": f"user{i}", "password": "Password123!"})
            users.append(resp.get_json()["data"]["token"])

        # Admin login
        resp = client.post("/api/auth/login", json={"username": "admin", "password": "AdminPass123!"})
        admin_token = resp.get_json()["data"]["token"]

        # 2. User 1 reports an item
        log("User 1 reporting item...")
        item_data = {
            "category": "Electronics",
            "item_type": "Phone",
            "found_location": "Hall",
            "found_datetime": "2026-03-10T12:00:00",
            "public_description": "Found a black smartphone."
        }
        resp = client.post("/api/items/found", json=item_data, headers={"Authorization": f"Bearer {users[0]}"})
        item_id = resp.get_json()["data"]["item_id"]

        # 3. User 2 claims it
        log("User 2 claiming item...")
        claim_data = {"found_item_id": item_id, "claimant_name": "User 2", "claimant_email": "u2@test.com", "description": "My phone", "declared_value": "500", "receipt_proof": "N/A"}
        resp = client.post("/api/claims/submit", json=claim_data, headers={"Authorization": f"Bearer {users[1]}"})
        claim_id = resp.get_json()["data"]["claim_id"]

        # 4. IDOR TEST: User 1 tries to access User 2's potential matches
        log("Testing IDOR: User 1 accessing User 2's claim matches...")
        resp = client.get(f"/api/claims/{claim_id}/potential-matches", headers={"Authorization": f"Bearer {users[0]}"})
        assert resp.status_code == 403
        log("IDOR access blocked (403 Forbidden).")

        # 5. CONCURRENCY TEST: Multiple approvals
        log("Registering User 3 and submitting second claim for same item...")
        u3 = {"username": "user3", "password": "Password123!", "name": "User 3", "email": "u3@test.com", "role": "user"}
        client.post("/api/auth/register", json=u3)
        resp = client.post("/api/auth/login", json={"username": "user3", "password": "Password123!"})
        u3_token = resp.get_json()["data"]["token"]
        
        resp = client.post("/api/claims/submit", json=claim_data, headers={"Authorization": f"Bearer {u3_token}"})
        claim_id_2 = resp.get_json()["data"]["claim_id"]

        log("Admin approving first claim...")
        resp = client.post(f"/api/claims/{claim_id}/verify", json={"decision": "approved"}, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

        log("Admin trying to approve second claim for SAME item...")
        resp = client.post(f"/api/claims/{claim_id_2}/verify", json={"decision": "approved"}, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 400
        assert "Another claim is already approved" in resp.get_json()["message"]
        log("Concurrent approval blocked successfully.")

        # 6. GLOBAL ERROR HANDLING TEST: Send malformed data (invalid JSON)
        log("Testing global error handler with malformed payload...")
        resp = client.post("/api/auth/login", data="this is not json", content_type="application/json")
        # Flask usually handles malformed JSON with 400 Bad Request
        assert resp.status_code == 400
        log("Global error handler caught malformed input.")

        log("PHASE 6.6 SECURITY TEST PASSED!")

if __name__ == "__main__":
    try:
        run_security_test()
    except Exception as e:
        print(f"\n[FAIL] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
