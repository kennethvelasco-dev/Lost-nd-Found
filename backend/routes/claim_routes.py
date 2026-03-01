from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.services.claim_service import (
    submit_claim,
    get_potential_matches_service,
    link_claim_service,
    schedule_pickup_service
)
from backend.models.claims import (
    get_pending_claims,
    verify_claim,
    ValidationError
)
from backend.helpers.response import success_response, error_response

claim_bp = Blueprint("claims", __name__)

@claim_bp.route("/submit", methods=["POST"])
@jwt_required()
def post_claim():
    """Submit a claim for a found item or a general report."""
    user_id = get_jwt_identity()
    data = request.get_json()
    result, status = submit_claim(data, user_id)
    return jsonify(success_response(result)), status

@claim_bp.route("/pending", methods=["GET"])
@jwt_required()
def get_pending():
    """Get all pending claims."""
    claims = get_pending_claims()
    return jsonify(success_response(claims)), 200

@claim_bp.route("/<int:claim_id>/verify", methods=["POST"])
@jwt_required()
def post_verify_claim(claim_id):
    """Approve or reject a claim. Admin only."""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify(error_response("FORBIDDEN", "Admin access required")), 403

    data = request.get_json()
    decision = data.get("decision")
    admin_username = get_jwt_identity()
    result, status = verify_claim(claim_id, decision, admin_username)
    return jsonify(success_response(result)), status

@claim_bp.route("/<int:claim_id>/potential-matches", methods=["GET"])
@jwt_required()
def get_matches(claim_id):
    """Get potential items matching a claim."""
    result, status = get_potential_matches_service(claim_id)
    return jsonify(success_response(result)), status

@claim_bp.route("/<int:claim_id>/link", methods=["POST"])
@jwt_required()
def post_link_claim(claim_id):
    """Link a general claim/report to a found item."""
    data = request.get_json()
    found_item_id = data.get("found_item_id")
    result, status = link_claim_service(claim_id, found_item_id)
    return jsonify(success_response(result)), status

@claim_bp.route("/<int:claim_id>/schedule", methods=["POST"])
@jwt_required()
def post_schedule_pickup(claim_id):
    """Schedule a pickup for an approved claim."""
    data = request.get_json()
    result, status = schedule_pickup_service(claim_id, data)
    return jsonify(success_response(result)), status

@claim_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify(error_response("VALIDATION_ERROR", e.message)), e.status_code
