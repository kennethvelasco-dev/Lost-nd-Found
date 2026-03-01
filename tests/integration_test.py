
import sys
import json
from datetime import datetime, timezone
from backend import create_app
print(f"DEBUG: backend file: {create_app.__module__}")
import backend
print(f"DEBUG: backend path: {backend.__path__}")
from backend.models.base import get_db_connection, init_db, DataBase
from backend.helpers.user_helpers import create_default_admin
import os

def log(msg):
    print(f"\n[TEST] {msg}")

def fail(msg):
    print(f"\n[FAIL] {msg}")
    sys.exit(1)

def run_integration_test():
    app = create_app()
    client = app.test_client()
    
    with app.app_context():
        # 1. Setup
        log("Setting up Database...")
        if os.path.exists(DataBase):
            os.remove(DataBase)
            print(f"Deleted existing database at {DataBase}")

        init_db()
        create_default_admin() # Creates admin/AdminPass123!

        # 2. User Registration & Login
        log("Registering & Logging in User...")
        user_data = {
            "username": "testuser", 
            "password": "Password123!",
            "name": "Test User",
            "email": "test@test.com",
            "role": "user"
        }
        resp = client.post("/api/register", json=user_data)
        if resp.status_code != 201:
            fail(f"Registration failed: {resp.get_json()}")
        
        resp = client.post("/api/login", json={"username": "testuser", "password": "Password123!"})
        if resp.status_code != 200:
            fail(f"Login failed: {resp.get_json()}")
        
        user_token = resp.get_json()["data"]["token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 3. Admin Login
        log("Logging in Admin...")
        resp = client.post("/api/login", json={"username": "admin", "password": "AdminPass123!"})
        admin_token = resp.get_json()["data"]["token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 4. Post Found Item (by User)
        log("Posting Found Item (User)...")
        found_item = {
            "category": "Electronics", 
            "item_type": "Phone",
            "found_location": "Cafeteria", 
            "found_datetime": datetime.now(timezone.utc).isoformat(),
            "brand": "Apple",
            "color": "White",
            "public_description": "White iPhone found on table"
        }
        resp = client.post("/api/found", json=found_item, headers=user_headers)
        if resp.status_code != 201:
            fail(f"Found item post failed: {resp.get_json()}")
        
        found_item_id = resp.get_json()["data"]["item_id"]
        print(f"Found Item ID: {found_item_id}")

        # 5. Post Lost Item (by User)
        log("Posting Lost Item (User)...")
        lost_item = {
            "category": "Electronics",
            "item_type": "Phone",
            "brand": "Apple",
            "color": "White",
            "last_seen_location": "Library",
            "last_seen_datetime": datetime.now(timezone.utc).isoformat(),
            "public_description": "Lost my white iPhone",
            "private_details": "Serial number: SN12345"
        }
        resp = client.post("/api/lost", json=lost_item, headers=user_headers)
        if resp.status_code != 201:
            fail(f"Lost item post failed: {resp.get_json()}")
        print("Lost item posted successfully")

        # 6. Search Items
        log("Testing Search...")
        # 6a. Public search for found electronics
        resp = client.get("/api/search?category=Electronics&status=found", headers=user_headers)
        search_results = resp.get_json()["data"]
        if not search_results:
            fail("Search for found electronics returned nothing")
        print(f"Found {len(search_results)} found items")

        # 6b. Search with query
        resp = client.get("/api/search?query=iPhone", headers=user_headers)
        search_results = resp.get_json()["data"]
        if not any(item["item_type"] == "Phone" for item in search_results):
            fail("Search for 'iPhone' did not return the expected phone")
        print("Search by query passed")

        # 7. Admin Post Found Item
        log("Admin Posting Found Item...")
        admin_found_item = {
            "category": "Accessories",
            "item_type": "Watch",
            "found_location": "Office",
            "found_datetime": datetime.now(timezone.utc).isoformat(),
            "public_description": "Found a watch in the office storage"
        }
        resp = client.post("/api/items/found", json=admin_found_item, headers=admin_headers)
        if resp.status_code != 201:
            fail(f"Admin found item post failed: {resp.get_json()}")
        print("Admin reporting works")

        # 8. Submit Claim
        log("Submitting Claim...")
        claim_data = {
            "found_item_id": found_item_id,
            "claimant_name": "Test User",
            "claimant_email": "test@example.com",
            "answers": "It is mine",
            "receipt_proof": "http://img.com/receipt.jpg",
            "description": "I left it there",
            "declared_value": 500
        }
        resp = client.post("/api/claim", json=claim_data, headers=user_headers)
        if resp.status_code != 201:
            fail(f"Claim failed: {resp.get_json()}")
        claim_id = resp.get_json()["data"]["claim_id"]

        # 9. Admin Verify & Complete
        log("Admin Approving Claim...")
        resp = client.post(f"/api/claims/{claim_id}/verify", json={"decision": "approved"}, headers=admin_headers)
        if resp.status_code != 200:
            fail(f"Approval failed: {resp.get_json()}")

        log("Admin Completing Transaction...")
        resp = client.post(f"/api/claims/{claim_id}/verify", json={"decision": "completed"}, headers=admin_headers)
        if resp.status_code != 200:
            fail(f"Completion failed: {resp.get_json()}")

        # 10. Verify Final Statuses in DB
        log("Final Data Check...")
        conn = get_db_connection()
        claim = conn.execute("SELECT decision FROM claims WHERE id=?", (claim_id,)).fetchone()
        item = conn.execute("SELECT status FROM found_items WHERE id=?", (found_item_id,)).fetchone()
        conn.close()

        if claim["decision"] != "completed":
            fail(f"Claim status {claim['decision']}, expected completed")
        if item["status"] != "returned":
            fail(f"Item status {item['status']}, expected returned")

        print("\n✅ API-LEVEL INTEGRATION TEST PASSED")

if __name__ == "__main__":
    run_integration_test()
