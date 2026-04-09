from ..models.claims import (
    get_claim_detail_db,
    get_filtered_claims_db,
    get_completed_claims,
    verify_claim
)
from ..models.validators import (
    require_fields,
    validate_claim_decision,
    ValidationError
)

def get_pending_claims_service():
    """Return pending claims"""
    claims = get_filtered_claims_db(status_filter=['pending'])
    return claims, 200

def get_completed_transactions_service():
    """Return all completed claims/transactions for reporting."""
    transactions = get_completed_claims()
    return transactions, 200

def process_claim_verification(claim_id: int, data: dict, admin_username: str):
    """Validate and verify claim with edge-case handling"""
    require_fields(data, ["decision"])
    validate_claim_decision(data["decision"])

    # Check if claim exists
    claim = get_claim_detail_db(claim_id)
    if not claim:
        raise ValidationError(f"Claim ID {claim_id} not found", 404)

    # Perform verification (passing handover_notes if present)
    result, status = verify_claim(
        claim_id=claim_id,
        decision=data["decision"],
        admin_username=admin_username,
        handover_notes=data.get("handover_notes")
    )
    return result, status

def get_admin_stats_service():
    """Return counts for the admin dashboard"""
    from ..models.base import get_db_connection
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM lost_items WHERE status = 'lost'")
        total_lost = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM found_items WHERE status = 'found'")
        total_found = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM claims WHERE decision = 'pending'")
        pending_claims = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM found_items WHERE status = 'returned'")
        resolved_items = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM lost_items WHERE status = 'returned'")
        resolved_items += cursor.fetchone()[0]
        
        return {
            "total_lost": total_lost,
            "total_found": total_found,
            "pending_claims": pending_claims,
            "resolved_items": resolved_items
        }, 200
    finally:
        conn.close()