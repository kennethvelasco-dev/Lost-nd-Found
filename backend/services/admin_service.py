from backend.models.claims import get_claim_by_id 
from backend.models import (
    get_pending_claims,
    get_completed_claims,
    verify_claim,
    require_fields,
    validate_claim_decision,
    ValidationError
)

def get_pending_claims_service():
    """Return pending claims"""
    claims = get_pending_claims()
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
    claim = get_claim_by_id(claim_id)
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