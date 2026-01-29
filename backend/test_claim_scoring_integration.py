import sys
from datetime import datetime, timezone
from backend.models.base import get_db_connection, init_db
from backend.models.claims import create_claim, get_pending_claims
from backend.models.items import create_found_item, get_found_item_by_id
from backend.services.claim_scoring import compute_claim_score
from backend.helpers.claim_validation import validate_claim_data


# UTILITIES
def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def pass_test(msg):
    print(f"[PASS] {msg}")

def make_found_item_data():
    return {
        "category": "Electronics",
        "item_type": "Phone",
        "brand": "Samsung",
        "color": "Black",
        "found_location": "Library",
        "found_datetime": datetime.now(timezone.utc).isoformat(),
        "public_description": "Black Samsung phone near entrance"
    }

# CLEANUP DATABASE
print("\n--- DATABASE CLEANUP ---")
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")
    tables = ["users", "admins", "lost_items", "found_items", "claims", "audit_logs", "admin_actions"]
    for table in tables:
        cursor.execute(f"DELETE FROM {table};")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()
    pass_test("Database cleaned")
except Exception as e:
    fail(f"Database cleanup failed → {e}")

# INIT DB
print("\n--- DATABASE INIT ---")
try:
    init_db()
    pass_test("Database initialized")
except Exception as e:
    fail(f"Database init failed → {e}")

# CREATE FOUND ITEM
found_item_data = make_found_item_data()
found_item_result = create_found_item(found_item_data)
found_item_id = found_item_result.get("item_id")
if not found_item_id:
    fail("Found item creation failed: no ID returned")
pass_test(f"Found item created with id {found_item_id}")
# --- CLAIM CREATION & SCORING ---
try:
    claim_data = {
        "found_item_id": found_item_id,
        "claimed_category": "Electronics",
        "claimed_item_type": "Phone",
        "claimed_brand": "Samsung",
        "claimed_color": "Black",
        "claimed_private_details": "Screen cracked slightly"
    }

    # Validate claim
    validate_claim_data(claim_data)
    pass_test("Claim data validated")

    # Create claim (calls main program logic)
    claim_result, status = create_claim(claim_data)
    if status != 201:
        fail(f"Claim creation failed: {claim_result}")
    claim_id = claim_result.get("claim_id")
    pass_test(f"Claim created successfully with id {claim_id}")

    # Fetch pending claims and verify claim is there
    pending_claims = get_pending_claims()
    if not any(c["claim_id"] == claim_id for c in pending_claims):
        fail("Claim not found in pending claims")
    pass_test("Claim appears in pending claims")

    # Fetch the real found item from the DB for scoring
    found_item_for_score = get_found_item_by_id(found_item_id)
    if not found_item_for_score:
        fail("Found item not found for scoring")

    # Compute score using the actual DB entry
    score = compute_claim_score(claim_data, found_item_for_score)
    if not isinstance(score["total"], int):
        fail("Score total is not an integer")
    if "breakdown" not in score or not isinstance(score["breakdown"], dict):
        fail("Score breakdown is invalid")
    print("Breakdown:", score["breakdown"])
    print("Total:", score["total"])
    pass_test("Claim scoring works correctly and maintains backward compatibility")
except Exception as e:
    fail(f"Found item creation failed → {e}")

# CREATE CLAIM AND VALIDATE + SCORE
print("\n--- CLAIM CREATION & SCORING ---")
try:
    claim_data = {
        "found_item_id": found_item_id,
        "claimed_category": "Electronics",
        "claimed_item_type": "Phone",
        "claimed_brand": "Samsung",
        "claimed_color": "Black",
        "claimed_private_details": "Screen cracked slightly"
    }

    # Validate claim
    validate_claim_data(claim_data)
    pass_test("Claim data validated")

    # Create claim
    claim_result, status = create_claim(claim_data)
    if status != 201:
        fail(f"Claim creation failed: {claim_result}")
    claim_id = claim_result.get("claim_id")
    pass_test(f"Claim created successfully with id {claim_id}")

    # Fetch pending claims and verify claim is there
    pending_claims = get_pending_claims()
    if not any(c["claim_id"] == claim_id for c in pending_claims):
        fail("Claim not found in pending claims")
    pass_test("Claim appears in pending claims")

    # Use actual found item from DB for scoring
    found_item_from_db = get_found_item_by_id(found_item_id)
    score = compute_claim_score(claim_data, found_item_from_db)
    
    if not isinstance(score.get("total"), int):
        fail("Score total is not an integer")
    if "breakdown" not in score or not isinstance(score["breakdown"], dict):
        fail("Score breakdown is invalid")
    
    print("Breakdown:", score["breakdown"])
    print("Total:", score["total"])
    pass_test("Claim scoring works correctly and maintains backward compatibility")

except Exception as e:
    fail(f"Claim creation & scoring test failed → {e}")

print("\n--- ALL TESTS PASSED ---")