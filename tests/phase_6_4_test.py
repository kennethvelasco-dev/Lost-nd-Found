import sys
import json
from datetime import datetime, timezone
from backend import create_app
from backend.models.base import get_db_connection, init_db, DataBase
from backend.helpers.user_helpers import create_default_admin
import os

def log(msg):
    print(f"\n[PHASE 6.4 TEST] {msg}")

def run_phase_6_4_test():
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
            "username": "user64",
            "password": "Password123!",
            "name": "User 64",
            "email": "user64@test.com",
            "role": "user"
        }
        resp = client.post("/api/auth/register", json=user_data)
        assert resp.status_code == 201

        # 3. Login
        log("Logging in...")
        resp = client.post("/api/auth/login", json={"username": "user64", "password": "Password123!"})
        user_token = resp.get_json()["data"]["token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        resp = client.post("/api/auth/login", json={"username": "admin", "password": "AdminPass123!"})
        admin_token = resp.get_json()["data"]["token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 4. Admin reports found item
        log("Admin reporting found item...")
        found_item = {
            "category": "Keys",
            "item_type": "Car Key",
            "brand": "Toyota",
            "color": "Black",
            "found_location": "Parking Lot A",
            "found_datetime": "2026-03-02T08:00:00",
            "public_description": "Found a Toyota key fob."
        }
        resp = client.post("/api/items/found", json=found_item, headers=admin_headers)
        found_item_id = resp.get_json()["data"]["item_id"]

        # 5. User claims it
        log("User submitting claim...")
        claim_data = {
            "found_item_id": found_item_id,
            "claimant_name": "User 64",
            "claimant_email": "user64@test.com",
            "description": "Lost my Toyota key fob this morning.",
            "declared_value": "150",
            "receipt_proof": "N/A"
        }
        resp = client.post("/api/claims/submit", json=claim_data, headers=user_headers)
        claim_id = resp.get_json()["data"]["claim_id"]

        # 6. Admin approves claim
        log("Admin approving claim...")
        resp = client.post(f"/api/claims/{claim_id}/verify", json={"decision": "approved"}, headers=admin_headers)
        assert resp.status_code == 200

        # 7. Admin completes transaction with handover notes
        log("Admin completing transaction with handover notes...")
        completion_data = {
            "decision": "completed",
            "handover_notes": "Verified owner via key fob unlock test. User provided matching ID."
        }
        resp = client.post(f"/api/admin/claims/{claim_id}/verify", json=completion_data, headers=admin_headers)
        assert resp.status_code == 200
        log("Handover completed successfully.")

        # 8. Verify item status using search API
        log("Verifying item status is 'returned' using Search API...")
        resp = client.get("/api/items/search?status=returned", headers=user_headers)
        items = resp.get_json()["data"]
        # Find our item
        my_item = next(i for i in items if i["id"] == found_item_id)
        assert my_item["status"] == "returned"
        log("Item status correctly updated to 'returned'.")

        # 9. Verify reporting
        log("Fetching transaction report list...")
        resp = client.get("/api/admin/reports/transactions", headers=admin_headers)
        assert resp.status_code == 200
        transactions = resp.get_json()["data"]
        assert len(transactions) >= 1
        assert transactions[0]["claim_id"] == claim_id
        assert transactions[0]["handover_notes"] == completion_data["handover_notes"]

        log(f"Fetching detailed report for transaction {claim_id}...")
        resp = client.get(f"/api/admin/reports/transactions/{claim_id}", headers=admin_headers)
        assert resp.status_code == 200
        report = resp.get_json()["data"]
        assert report["transaction_id"] == claim_id
        assert report["item_details"]["category"] == "Keys"
        assert report["claimant_details"]["name"] == "User 64"
        assert "completed_at" in report
        
        log("PHASE 6.4 INTEGRATION TEST PASSED!")

if __name__ == "__main__":
    try:
        run_phase_6_4_test()
    except Exception as e:
        print(f"\n[FAIL] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
