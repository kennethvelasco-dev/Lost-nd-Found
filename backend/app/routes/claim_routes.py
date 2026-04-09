from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..services.claim_service import (
    submit_claim,
    get_potential_matches_service,
    link_claim_service,
    schedule_pickup_service,
    get_user_claims_service,
    get_claim_detail_service
)
from ..models.claims import (
    get_filtered_claims_db,
    verify_claim,
    ValidationError
)
from ..utils.response import success_response, error_response

from ..utils.production_safety import require_json_fields

claim_bp = Blueprint("claims", __name__)

@claim_bp.route("/submit", methods=["POST"])
@claim_bp.route("", methods=["POST"]) # Alias for fallback/compatibility
@jwt_required()
@require_json_fields(["found_item_id", "description", "color"])
def post_claim():
    """Submit a claim for a found item or a general report."""
    user_id = get_jwt_identity()
    data = request.get_json()
    result, status = submit_claim(data, user_id)
    if status >= 400:
        return jsonify(error_response("CLAIM_ERROR", result.get("error", "Submission failed"))), status
    return jsonify(success_response(result)), status

@claim_bp.route("/pending", methods=["GET"])
@jwt_required()
def get_pending():
    """Get pending claims restricted by ownership/role."""
    user_id = get_jwt_identity()
    role = get_jwt().get("role", "user")
    
    # Get status filter from query param if admin
    status_param = request.args.get("status")
    status_filter = [status_param] if status_param else None
    
    claims, status = get_user_claims_service(user_id, role, status_filter=status_filter)
    return jsonify(success_response(claims)), status

@claim_bp.route("/<int:claim_id>/verify", methods=["POST"])
@jwt_required()
@require_json_fields(["decision"])
def post_verify_claim(claim_id):
    """Approve or reject a claim. Admin only."""
    # Note: Using get_jwt() instead of re-importing in function for consistency
    jwt_claims = get_jwt()
    if jwt_claims.get("role") != "admin":
        return jsonify(error_response("FORBIDDEN", "Admin access required")), 403

    data = request.get_json()
    decision = data.get("decision")
    admin_username = get_jwt_identity()
    result, status = verify_claim(claim_id, decision, admin_username)
    
    if status >= 400:
        return jsonify(error_response("VERIFICATION_ERROR", result.get("error", "Error"))), status
        
    return jsonify(success_response(result)), status

@claim_bp.route("/<int:claim_id>", methods=["GET"])
@jwt_required()
def get_claim_detail(claim_id):
    """Get details for a specific claim. Owner or Admin only."""
    user_id = get_jwt_identity()
    role = get_jwt().get("role", "user")
    result, status = get_claim_detail_service(claim_id, user_id, role)
    if status >= 400:
        return jsonify(error_response("CLAIM_DETAIL_ERROR", result.get("error", "Could not retrieve claim details"))), status
    return jsonify(success_response(result)), status

@claim_bp.route("/<int:claim_id>/potential-matches", methods=["GET"])
@jwt_required()
def get_matches(claim_id):
    """Get potential items matching a claim. Owner or Admin only."""
    user_id = get_jwt_identity()
    role = get_jwt().get("role", "user")
    result, status = get_potential_matches_service(claim_id, user_id, role)
    return jsonify(success_response(result)), status

@claim_bp.route("/<int:claim_id>/link", methods=["POST"])
@jwt_required()
def post_link_claim(claim_id):
    """Link a general claim/report to a found item. Owner or Admin only."""
    user_id = get_jwt_identity()
    role = get_jwt().get("role", "user")
    data = request.get_json()
    found_item_id = data.get("found_item_id")
    result, status = link_claim_service(claim_id, found_item_id, user_id, role)
    return jsonify(success_response(result)), status

@claim_bp.route("/<int:claim_id>/schedule", methods=["POST"])
@jwt_required()
def post_schedule_pickup(claim_id):
    """Schedule a pickup for an approved claim. Owner or Admin only."""
    user_id = get_jwt_identity()
    role = get_jwt().get("role", "user")
    data = request.get_json()
    result, status = schedule_pickup_service(claim_id, data, user_id, role)
    return jsonify(success_response(result)), status

@claim_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify(error_response("VALIDATION_ERROR", e.message)), e.status_code
