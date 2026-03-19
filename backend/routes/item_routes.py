from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.item_service import (
    submit_found_item,
    submit_lost_item,
    get_found_items,
    search_items_service
)
from backend.helpers.response import error_response, success_response
from backend.models import ValidationError

item_bp = Blueprint("items", __name__)

@item_bp.route("/lost", methods=["POST"])
@jwt_required()
def report_lost_item():
    data = request.json or {}
    try:
        identity = get_jwt_identity()
        result, status = submit_lost_item(data, identity)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code

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
            return jsonify(error_response("VALIDATION_ERROR", ve.message)), ve.status_code
        
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)
    result, status = get_found_items(limit, offset)
    return jsonify(success_response(result)), status

@item_bp.route("/search", methods=["GET"])
@jwt_required()
def search_items_route():
    filters = request.args.to_dict()
    # Ensure limit/offset are integers if provided
    if "limit" in filters: filters["limit"] = int(filters["limit"])
    if "offset" in filters: filters["offset"] = int(filters["offset"])
    
    try:
        result, status = search_items_service(filters)
        return jsonify(success_response(result)), status
    except Exception as e:
        return jsonify(error_response("INTERNAL_ERROR", str(e))), 500

@item_bp.route("/pending", methods=["GET"])
@jwt_required()
def get_pending_reports():
    """Get reports awaiting approval. Admin only."""
    # Note: Role check should ideally be in a decorator or service
    from flask_jwt_extended import get_jwt
    if get_jwt().get("role") != "admin":
        return jsonify(error_response("FORBIDDEN", "Admin access required")), 403
    
    from backend.services.item_service import get_pending_reports_service
    result, status = get_pending_reports_service()
    return jsonify(success_response(result)), status

@item_bp.route("/reports/<int:id>/verify", methods=["POST"])
@jwt_required()
def verify_report_route(id):
    """Approve or reject a report. Admin only."""
    from flask_jwt_extended import get_jwt
    if get_jwt().get("role") != "admin":
        return jsonify(error_response("FORBIDDEN", "Admin access required")), 403
    
    data = request.json or {}
    require_fields(data, ["decision", "type"])
    
    from backend.services.item_service import verify_report_service
    admin_username = get_jwt_identity()
    result, status = verify_report_service(
        id, 
        data["type"], 
        data["decision"], 
        data.get("reason", ""), 
        admin_username
    )
    return jsonify(success_response(result)), status

@item_bp.route("/my-activities", methods=["GET"])
@jwt_required()
def get_my_activities():
    """Get reports and claims for the current user."""
    user_id = get_jwt_identity()
    from backend.services.item_service import get_user_activities_service
    result, status = get_user_activities_service(user_id)
    return jsonify(success_response(result)), status
