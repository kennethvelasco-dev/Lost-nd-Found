from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from backend.services.admin_service import (
    get_pending_claims_service, 
    process_claim_verification
)
from backend.services.item_service import submit_admin_found_item
from backend.services.reporting_service import (
    get_transaction_summary,
    get_all_completed_transactions_report
)
from backend.helpers.response import success_response, error_response
from backend.models import ValidationError

admin_bp = Blueprint("admin", __name__)

# Thin admin check decorator
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Ensure a valid JWT exists first
            verify_jwt_in_request()
            claims = get_jwt()
        except Exception:
            return jsonify(error_response("UNAUTHORIZED", "Invalid or missing token")), 401

        if claims.get("role") != "admin":
            return jsonify(error_response("FORBIDDEN", "Admin access required")), 403

        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route("/claims", methods=["GET"])
@jwt_required()
@admin_required
def view_claims():
    try:
        claims, status = get_pending_claims_service()
        return jsonify(success_response(claims)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code


@admin_bp.route("/claims/<int:claim_id>/verify", methods=["POST"])
@jwt_required()
@admin_required
def verify_claim_route(claim_id):
    data = request.json or {}
    try:
        admin_user_id = get_jwt_identity()
        result, status = process_claim_verification(
            claim_id, data, admin_user_id
        )
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code

@admin_bp.route("/items/found", methods=["POST"])
@jwt_required()
@admin_required
def admin_report_found_item():
    data = request.json or {}
    try:
        admin_id = get_jwt_identity()
        result, status = submit_admin_found_item(data, admin_id)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code

# REPORTING ENDPOINTS
@admin_bp.route("/reports/transactions", methods=["GET"])
@jwt_required()
@admin_required
def get_transactions_list():
    """List all completed transactions."""
    transactions, status = get_all_completed_transactions_report()
    return jsonify(success_response(transactions)), status

@admin_bp.route("/reports/transactions/<int:claim_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_transaction_report(claim_id):
    """Get detailed report for one transaction."""
    report, status = get_transaction_summary(claim_id)
    return jsonify(success_response(report) if status == 200 else report), status
