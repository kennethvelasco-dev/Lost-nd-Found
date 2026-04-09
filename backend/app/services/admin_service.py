from ..models.claims import (
    get_claim_detail_db,
    get_filtered_claims_db,
    get_all_completed_claims_db,
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
    transactions = get_all_completed_claims_db()
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
    from ..models.items import get_dashboard_stats_db
    stats = get_dashboard_stats_db()
    return stats, 200