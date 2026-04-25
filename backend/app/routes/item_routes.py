from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..utils.decorators import admin_required
from ..extensions import limiter
from ..services.item_service import (
    submit_found_item,
    submit_lost_item,
    get_found_items,
    search_items_service,
    get_item_detail_service,
    get_pending_reports_service,
    verify_report_service,
    get_user_activities_service,
    dismiss_activity_service,
)
from ..utils.response import error_response, success_response
from ..models import ValidationError
from ..utils.production_safety import require_json_fields

item_bp = Blueprint("items", __name__)


@item_bp.route("/<string:report_id>", methods=["GET"])
@jwt_required()
def get_item_detail_route(report_id):
    """Get unified item detail by UUID."""
    result, status = get_item_detail_service(report_id)
    return jsonify(success_response(result)), status


@item_bp.route("/lost", methods=["GET", "POST"])
@jwt_required()
def lost_items_route():
    if request.method == "POST":

        @require_json_fields(["category", "last_seen_location", "last_seen_datetime"])
        def process_post():
            data = request.json or {}
            try:
                identity = get_jwt_identity()
                result, status = submit_lost_item(data, identity)
                return jsonify(success_response(result)), status
            except ValidationError as ve:
                return (
                    jsonify(error_response("VALIDATION_ERROR", ve.message)),
                    ve.status_code,
                )

        return process_post()

    # GET logic
    filters = request.args.to_dict()
    filters["status"] = "lost"
    result, status = search_items_service(filters)
    return jsonify(success_response(result)), status


@item_bp.route("/found", methods=["GET", "POST"])
@jwt_required()
def found_items():
    if request.method == "POST":
        data = request.json or {}
        try:
            identity = get_jwt_identity()
            result, status = submit_found_item(data, identity)
            return jsonify(success_response(result)), status
        except ValidationError as ve:
            return (
                jsonify(error_response("VALIDATION_ERROR", ve.message)),
                ve.status_code,
            )

    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)
    result, status = get_found_items(limit, offset)
    return jsonify(success_response(result)), status


@item_bp.route("/search", methods=["GET"])
@jwt_required()
def search_items_route():
    filters = request.args.to_dict()
    # Ensure limit/offset are integers if provided
    if "limit" in filters:
        filters["limit"] = int(filters["limit"])
    if "offset" in filters:
        filters["offset"] = int(filters["offset"])

    try:
        result, status = search_items_service(filters)
        return jsonify(success_response(result)), status
    except Exception as e:
        return jsonify(error_response("INTERNAL_ERROR", str(e))), 500


@item_bp.route("/pending", methods=["GET"])
@jwt_required()
@admin_required
def get_pending_reports():
    """Get reports awaiting approval. Admin only."""
    result, status = get_pending_reports_service()
    return jsonify(success_response(result)), status


@item_bp.route("/reports/<int:id>/verify", methods=["POST"])
@jwt_required()
@admin_required
@require_json_fields(["decision", "type"])
def verify_report_route(id):
    """Approve or reject a report. Admin only."""
    data = request.json or {}
    admin_username = get_jwt_identity()
    result, status = verify_report_service(
        id, data["type"], data["decision"], data.get("reason", ""), admin_username
    )
    if status >= 400:
        return (
            jsonify(
                error_response(
                    "VERIFICATION_ERROR", result.get("error", "Action failed")
                )
            ),
            status,
        )

    return (
        jsonify(
            success_response(result, message=f"Report {data['decision']} successfully")
        ),
        status,
    )


@item_bp.route("/my-activities", methods=["GET"])
@jwt_required()
def get_my_activities():
    """Get reports and claims for the current user."""
    user_id = get_jwt_identity()
    result, status = get_user_activities_service(user_id)
    return jsonify(success_response(result)), status


@item_bp.route("/reports/<string:type>/<int:id>/dismiss", methods=["POST"])
@jwt_required()
def dismiss_report_route(type, id):
    """Dismiss a report from the user's view."""
    user_id = get_jwt_identity()
    result, status = dismiss_activity_service(id, type, user_id)
    return jsonify(success_response(result)), status


@item_bp.route("/claims/<int:id>/dismiss", methods=["POST"])
@jwt_required()
def dismiss_claim_route(id):
    """Dismiss a claim from the user's view."""
    user_id = get_jwt_identity()
    result, status = dismiss_activity_service(id, "claim", user_id)
    return jsonify(success_response(result)), status


@item_bp.route("/returned", methods=["GET"])
@item_bp.route("/released", methods=["GET"])
@jwt_required()
def get_returned_items_route():
    """Get all released/returned items from the dedicated storage."""
    filters = request.args.to_dict()
    try:
        from ..services.item_service import get_released_items_service

        result, status = get_released_items_service(filters)
        return jsonify(success_response(result)), status
    except Exception as e:
        return jsonify(error_response("INTERNAL_ERROR", str(e))), 500


@item_bp.route("/released/<string:report_id>", methods=["GET"])
@jwt_required()
def get_released_item_detail_route(report_id):
    """
    Get the released snapshot for a specific original report_id (lost/found).
    Used by ItemDetail to show return log (claimant, notes, proof, etc.).
    """
    try:
        from ..services.item_service import get_released_item_detail_service

        result, status = get_released_item_detail_service(report_id)
        if status >= 400:
            return (
                jsonify(
                    error_response(
                        "NOT_FOUND", result.get("error", "Released item not found")
                    )
                ),
                status,
            )
        return jsonify(success_response(result)), status
    except Exception as e:
        return jsonify(error_response("INTERNAL_ERROR", str(e))), 500


@item_bp.route("/released/<int:released_id>", methods=["GET"])
@limiter.limit("200 per hour")
def get_public_released_detail(released_id):
    """Public detail view for a specific released item by its ID.
    Accessible to non-admin users (read-only).
    """
    from ..models.items import get_released_item_by_id_db

    item = get_released_item_by_id_db(released_id)
    if not item:
        return jsonify(error_response("NOT_FOUND", "Released item not found")), 404
    return jsonify(success_response(item)), 200
