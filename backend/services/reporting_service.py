from backend.models.claims import get_claim_by_id, get_completed_claims
from backend.models.items import get_found_item_by_id
from backend.models.base import get_db_connection

def get_transaction_summary(claim_id: int):
    """
    Generates a detailed report of a completed transaction.
    """
    claim = get_claim_by_id(claim_id)
    if not claim:
        return {"error": "Claim not found"}, 404
    
    if claim["decision"] != "completed":
        return {"error": "Transaction not completed yet"}, 400
        
    found_item = get_found_item_by_id(claim["found_item_id"])
    
    # Fetch user info for the claimant
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        user_row = cursor.execute("SELECT username, name, email FROM users WHERE id = ?", (claim["user_id"],)).fetchone()
        user = dict(user_row) if user_row else {}
    finally:
        conn.close()

    report = {
        "transaction_id": claim["id"],
        "completed_at": claim["completed_at"],
        "handover_notes": claim["handover_notes"],
        "claimant_details": {
            "name": claim["claimant_name"],
            "email": claim["claimant_email"],
            "system_username": user.get("username")
        },
        "item_details": {
            "report_id": found_item["report_id"],
            "category": found_item["category"],
            "item_type": found_item["item_type"],
            "brand": found_item["brand"],
            "color": found_item["color"],
            "found_location": found_item["found_location"],
            "found_datetime": found_item["found_datetime"]
        },
        "pickup_details": {
            "datetime": claim["pickup_datetime"],
            "location": claim["pickup_location"]
        }
    }
    
    return report, 200

def get_all_completed_transactions_report():
    """
    Returns a list of all completed transactions with brief info.
    """
    claims = get_completed_claims()
    return claims, 200
