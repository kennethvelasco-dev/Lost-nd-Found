from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.decorators import admin_required
from ..services.admin_service import (
    get_pending_claims_service,
    process_claim_verification,
    get_admin_stats_service,
)
from ..services.item_service import submit_admin_found_item, resolve_item_service
from ..utils.response import success_response, error_response
from ..models import ValidationError
from ..services.reporting_service import (
    get_transaction_summary,
    get_all_completed_transactions_report,
)
from ..extensions import limiter

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/claims", methods=["GET"])
@jwt_required()
@admin_required
@limiter.limit("50 per 15 minutes")
def view_claims():
    try:
        claims, status = get_pending_claims_service()
        return jsonify(success_response(claims)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code


@admin_bp.route("/claims/<int:claim_id>/verify", methods=["POST"])
@jwt_required()
@admin_required
@limiter.limit("50 per 15 minutes")
def verify_claim_route(claim_id):
    data = request.json or {}
    try:
        admin_user_id = get_jwt_identity()
        result, status = process_claim_verification(claim_id, data, admin_user_id)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code


@admin_bp.route("/items/found", methods=["POST"])
@jwt_required()
@admin_required
@limiter.limit("50 per 15 minutes")
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
@limiter.limit("50 per 15 minutes")
def get_transactions_list():
    """List all completed transactions."""
    transactions, status = get_all_completed_transactions_report()
    return jsonify(success_response(transactions)), status


@admin_bp.route("/reports/transactions/<int:claim_id>", methods=["GET"])
@jwt_required()
@admin_required
@limiter.limit("50 per 15 minutes")
def get_transaction_report(claim_id):
    """Get detailed report for one transaction."""
    report, status = get_transaction_summary(claim_id)
    return jsonify(success_response(report) if status == 200 else report), status


@admin_bp.route("/resolve-item", methods=["POST"])
@jwt_required()
@admin_required
@limiter.limit("50 per 15 minutes")
def resolve_item_route():
    """Manually log an item as returned. Admin only."""
    data = request.json or {}
    admin_username = get_jwt_identity()
    result, status = resolve_item_service(data, admin_username)
    if status >= 400:
        return (
            jsonify(error_response("RESOLUTION_ERROR", result.get("error", "Error"))),
            status,
        )
    return jsonify(success_response(result)), status


@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
@admin_required
@limiter.limit("50 per 15 minutes")
def get_stats_route():
    """Get system-wide stats for admin dashboard."""
    result, status = get_admin_stats_service()
    return jsonify(success_response(result)), status


@admin_bp.route("/released-items/<int:released_id>", methods=["GET"])
@jwt_required()
@admin_required
@limiter.limit("50 per 15 minutes")
def get_released_detail(released_id):
    """Fetch detail for a specific released item by its ID (admin view)."""
    from ..models.items import get_released_item_detail_view_db

    item = get_released_item_detail_view_db(released_id)
    if not item:
        return jsonify(error_response("NOT_FOUND", "Released item not found")), 404
    return jsonify(success_response(item)), 200
