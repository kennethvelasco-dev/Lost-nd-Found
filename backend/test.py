import sys
from datetime import datetime, timezone
from backend import create_app
from backend.models.base import get_db_connection, init_db
from backend.helpers.user_helpers import create_default_admin
from backend.services.auth_service import register_user, login_user, refresh_token, logout_token
from backend.models.items import create_found_item, get_found_item_by_id
from backend.models.claims import create_claim, get_pending_claims
from backend.services.scoring_service import compute_claim_score
from backend.helpers.input_validation import validate_claim_payload
from backend.models.audit import log_action

# ==========================
# Utilities
# ==========================
def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def pass_test(msg):
    print(f"[PASS] {msg}")

# ==========================
# Setup Flask app context
# ==========================
app = create_app()

with app.app_context():
    # ==========================
    # 0️⃣ Database Cleanup & Init
    # ==========================
    print("\n--- DATABASE CLEANUP & INIT ---")
    try:
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
        create_default_admin()
        pass_test("Database cleaned and initialized with default admin")
    except Exception as e:
        fail(f"Database init failed → {e}")

    # ==========================
    # 1️⃣ Register Users
    # ==========================
    print("\n--- USER REGISTRATION ---")
    users = [
        {"username": "user1", "password": "Password123!"},
        {"username": "user2", "password": "Password456!"}
    ]

    user_tokens = {}
    for u in users:
        try:
            res, status = register_user(u)
            user_tokens[u["username"]] = res["token"]
            print(f"Register user: {u['username']} → {res}")
            pass_test(f"User {u['username']} registered successfully")
        except Exception as e:
            fail(f"Register user {u['username']} failed → {e}")

    # ==========================
    # 2️⃣ Login Users
    # ==========================
    print("\n--- USER LOGIN ---")
    login_tokens = {}
    for u in users:
        try:
            res, status = login_user(u)
            login_tokens[u["username"]] = res["token"]
            print(f"Login user: {u['username']} → {res}")
            pass_test(f"User {u['username']} logged in successfully")
        except Exception as e:
            fail(f"Login failed for {u['username']} → {e}")

    # ==========================
    # 3️⃣ Refresh Token
    # ==========================
    print("\n--- TOKEN REFRESH ---")
    for uname, token in login_tokens.items():
        try:
            res, status = refresh_token({"user": uname})
            print(f"Token refresh for {uname} → {res}")
            pass_test(f"Token refresh works for {uname}")
        except Exception as e:
            fail(f"Token refresh failed for {uname} → {e}")

    # ==========================
    # 4️⃣ Logout Token
    # ==========================
    print("\n--- LOGOUT TOKEN ---")
    for uname, token in login_tokens.items():
        try:
            # Here we simulate using token jti; for testing, we just pass token string
            res, status = logout_token(token)
            print(f"Logout token for {uname} → {res}")
            pass_test(f"Logout works for {uname}")
        except Exception as e:
            fail(f"Logout failed for {uname} → {e}")

    # ==========================
    # 5️⃣ Create Found Item (user1)
    # ==========================
    print("\n--- CREATE FOUND ITEM ---")
    try:
        found_item_data = {
            "category": "Electronics",
            "item_type": "Phone",
            "brand": "Samsung",
            "color": "Black",
            "found_location": "Library",
            "found_datetime": datetime.now(timezone.utc).isoformat(),
            "public_description": "Black Samsung phone near entrance",
            "reporter_id": 1
        }
        res = create_found_item(found_item_data)
        found_item_id = res.get("item_id")
        print(f"Found item creation → {res}")
        pass_test("create_found_item is working successfully")
    except Exception as e:
        fail(f"create_found_item failed → {e}")

    # ==========================
    # 6️⃣ Validate Claim (user2)
    # ==========================
    print("\n--- CLAIM VALIDATION ---")
    claim_data = {
    "found_item_id": found_item_id,
    "claimant_name": "User Two",
    "claimant_email": "user2@test.com",
    "answers": "Yes it is mine",
    "claimed_category": "Electronics",
    "claimed_item_type": "Phone",
    "claimed_brand": "Samsung",
    "claimed_color": "Black",
    "claimed_private_details": "Screen slightly cracked",
    "receipt_proof": "receipt.pdf",
    "description": "Lost my Samsung phone near library",
    "declared_value": 500
    }


    try:
        validate_claim_payload(claim_data)
    except Exception as e:
        fail(f"Claim validation failed → {e}")
    print(f"Claim validation data → {claim_data}")
    pass_test("validate_claim_data is working successfully")

    # ==========================
    # 7️⃣ Create Claim
    # ==========================
    print("\n--- CREATE CLAIM ---")
    try:
        res, status = create_claim(claim_data)
        claim_id = res.get("claim_id")
        print(f"Claim creation → {res}")
        pass_test("create_claim is working successfully")
    except Exception as e:
        fail(f"create_claim failed → {e}")

    # ==========================
    # 8️⃣ Get Pending Claims
    # ==========================
    print("\n--- GET PENDING CLAIMS ---")
    try:
        pending = get_pending_claims()
        print(f"Pending claims → {pending}")
        pass_test("get_pending_claims is working successfully")
    except Exception as e:
        fail(f"get_pending_claims failed → {e}")

    # ==========================
    # 9️⃣ Claim Scoring
    # ==========================
    print("\n--- CLAIM SCORING ---")
    try:
        found_item_db = get_found_item_by_id(found_item_id)
        score = compute_claim_score(claim_data, found_item_db)
        print(f"Claim scoring breakdown → {score}")
        pass_test("compute_claim_score is working successfully")
    except Exception as e:
        fail(f"compute_claim_score failed → {e}")

    # ==========================
    # 1️⃣0️⃣ Audit Logging
    # ==========================
    print("\n--- AUDIT LOGGING ---")
    try:
        log_action(
            action="TEST_RUN",
            entity_type="claim",
            entity_id=claim_id,
            performed_by="test_runner",
            notes="Full QA integration test"
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE entity_id=?", (claim_id,))
        count = cursor.fetchone()[0]
        conn.close()
        print(f"Audit logs for claim → {count}")
        pass_test("log_action is working successfully")
    except Exception as e:
        fail(f"log_action failed → {e}")

    print("\n✅ FULL QA INTEGRATION TEST COMPLETED SUCCESSFULLY")