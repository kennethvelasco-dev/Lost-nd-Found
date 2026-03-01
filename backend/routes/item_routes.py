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
        
    items, status = get_found_items()
    return jsonify(success_response(items)), status

@item_bp.route("/search", methods=["GET"])
@jwt_required()
def search_items_route():
    filters = request.args.to_dict()
    try:
        items, status = search_items_service(filters)
        return jsonify(success_response(items)), status
    except Exception as e:
        return jsonify(error_response("INTERNAL_ERROR", str(e))), 500
