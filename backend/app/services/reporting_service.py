from ..models.claims import get_all_completed_claims_db, get_claims_db
from ..models.items import get_found_item_by_id, get_user_reports_db
from ..utils.user_helpers import get_user_by_id


def get_transaction_summary(user_id):
    """
    Returns counts and user-specific details for reports and claims.
    """
    user = get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}, 404

    user_info = {
        "username": user["username"],
        "name": user["name"],
        "email": user["email"],
    }

    reports = get_user_reports_db(user_id)
    claims = get_claims_db(user_id=user_id)

    return {
        "user": user_info,
        "counts": {"reports": len(reports), "claims": len(claims)},
    }, 200


def get_all_completed_transactions_report():
    """
    Generates a full history of successful returns for administrative view.
    """
    claims = get_all_completed_claims_db()
    report = []

    for claim in claims:
        found_item = get_found_item_by_id(claim["found_item_id"])
        if not found_item:
            continue

        user = get_user_by_id(claim["user_id"])

        entry = {
            "transaction_id": claim["id"],
            "resolution_date": claim["completed_at"] or claim["created_at"],
            "claimant_details": {
                "name": claim["claimant_name"],
                "email": claim["claimant_email"],
                "system_username": user["username"] if user else None,
            },
            "item_details": {
                "report_id": found_item["report_id"],
                "category": found_item["category"],
                "description": found_item["public_description"],
            },
            "handover_notes": claim["handover_notes"],
        }
        report.append(entry)

    return {"history": report}, 200
