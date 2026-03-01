
import sys
import json
from datetime import datetime, timezone
from backend import create_app
from backend.models.base import get_db_connection, init_db
from backend.helpers.user_helpers import create_default_admin
from backend.services.auth_service import register_user, login_user
from backend.models.items import create_found_item
from backend.models.claims import create_claim, get_pending_claims
from backend.services.admin_service import process_claim_verification
from backend.helpers.input_validation import validate_claim_payload

def log(msg):
    print(f"\n[TEST] {msg}")

def fail(msg):
    print(f"\n[FAIL] {msg}")
    sys.exit(1)

def run_integration_test():
    app = create_app()
    with app.app_context():
        # 1. Setup
        log("Setting up Database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")
        tables = ["users","admins","lost_items","found_items","claims","audit_logs","admin_actions"]
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        conn.close()
        
        init_db()
        create_default_admin() # Creates admin/AdminPass123!

        # 2. User Registration & Login
        log("Registering & Logging in User...")
        user_creds = {
            "username": "testuser", 
            "password": "Password123!",
            "name": "Test User",
            "email": "test@test.com",
            "role": "user"
        }
        register_user(user_creds)
        
        token_data, _ = login_user(user_creds)
        user_token = token_data["token"]
        print(f"User Token: {user_token[:20]}...")

        # 3. Admin Login
        log("Logging in Admin...")
        admin_creds = {"username": "admin", "password": "AdminPass123!"}
        admin_token_data, _ = login_user(admin_creds)
        admin_token = admin_token_data["token"]
        print(f"Admin Token: {admin_token[:20]}...")

        # 4. Post Found Item (by User)
        log("Posting Found Item...")
        found_item = {
            "category": "Electronics", 
            "item_type": "Phone",
            "found_location": "Cafeteria", 
            "found_datetime": datetime.now(timezone.utc).isoformat(),
            "brand": "Apple",
            "color": "White",
            "public_description": "White iPhone found on table",
            "reporter_id": 1,
            "reported_by": "testuser"
        }
        item_res = create_found_item(found_item)
        found_item_id = item_res["item_id"]
        print(f"Found Item ID: {found_item_id}")

        # 5. Submit Claim (by User)
        log("Submitting Claim...")
        claim_data = {
            "found_item_id": found_item_id,
            "claimant_name": "Test User",
            "claimant_email": "test@example.com",
            "answers": "Yes it is mine",
            "claimed_category": "Electronics",
            "claimed_item_type": "Phone",
            "claimed_brand": "Apple",
            "claimed_color": "White", 
            "receipt_proof": "http://example.com/receipt.jpg",
            "description": "Lost my white iPhone while eating",
            "declared_value": 999.99,
            "claimed_private_details": "Has a scratch on the back"
        }
        
        # Pre-validate
        try:
            validate_claim_payload(claim_data)
        except Exception as e:
            fail(f"Validation errors: {e}")

        claim_res, status = create_claim(claim_data)
        if status != 201:
            fail(f"Claim creation failed: {claim_res}")
            
        claim_id = claim_res["claim_id"]
        score = claim_res["score"]
        print(f"Claim ID: {claim_id}, Score: {score}")

        if score < 50:
            print("WARNING: Low score!")

        # 6. Admin View Pending Claims
        log("Admin Checking Pending Claims...")
        pending = get_pending_claims()
        if not pending:
            fail("No pending claims found!")
        
        target_claim = next((c for c in pending if c["claim_id"] == claim_id), None)
        if not target_claim:
            fail("Target claim not in pending list")
            
        print(f"Found pending claim score: {target_claim['score']}")

        # 7. Admin Verify Claim
        log("Admin Verifying Claim...")
        verify_data = {"decision": "approved"}
        verify_res, v_status = process_claim_verification(claim_id, verify_data, "admin")
        
        if v_status != 200:
            fail(f"Verification failed: {verify_res}")
            
        print(f"Verification Result: {verify_res}")

        # 9. Complete Transaction
        log("Completing Transaction...")
        complete_data = {"decision": "completed"}
        complete_res, c_status = process_claim_verification(claim_id, complete_data, "admin")
        
        if c_status != 200:
            fail(f"Completion failed: {complete_res}")
            
        print(f"Completion Result: {complete_res}")

        # 10. Verify Final Statuses
        log("Verifying Final Statuses...")
        conn = get_db_connection()
        claim_row = conn.execute("SELECT decision FROM claims WHERE id=?", (claim_id,)).fetchone()
        item_row = conn.execute("SELECT status FROM found_items WHERE id=?", (found_item_id,)).fetchone()
        
        if claim_row["decision"] != "completed":
            fail(f"Claim decision is {claim_row['decision']}, expected 'completed'")
        if item_row["status"] != "returned":
            fail(f"Item status is {item_row['status']}, expected 'returned'")
            
        conn.close()
        
        print("✅ INTEGRATION TEST PASSED (INCLUDING TRANSACTION COMPLETION)")

if __name__ == "__main__":
    run_integration_test()
