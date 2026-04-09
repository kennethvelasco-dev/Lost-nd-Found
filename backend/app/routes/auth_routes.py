from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..services.auth_service import register_user, login_user, refresh_token_service, logout_token
from ..utils.response import success_response, error_response
from ..models import ValidationError
from ..extensions import limiter
from ..utils.production_safety import require_json_fields

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
@require_json_fields(["username", "password", "role"])
def register():
    data = request.get_json() or {}
    try:
        result, status = register_user(data)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 400

from flask_jwt_extended import (
    jwt_required, 
    get_jwt_identity, 
    get_jwt, 
    set_access_cookies, 
    set_refresh_cookies, 
    unset_jwt_cookies
)

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
@require_json_fields(["username", "password"])
def login():
    data = request.get_json() or {}
    try:
        result, status = login_user(data)
        response = jsonify(success_response({
            "user": result["user"],
            "message": result["message"],
            "access_token": result["access_token"]
        }))
        
        # Set tokens in HTTP-only cookies
        set_access_cookies(response, result["access_token"])
        set_refresh_cookies(response, result["refresh_token"])
        
        return response, status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 401

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@limiter.limit("5 per minute")
def refresh():
    try:
        user_id = get_jwt_identity()
        role = get_jwt().get("role")
        old_jti = get_jwt()["jti"]
        
        # RTR: Generate new tokens
        result, status = refresh_token_service(user_id, role)
        
        response = jsonify(success_response({"message": "Token refreshed"}))
        set_access_cookies(response, result["access_token"])
        set_refresh_cookies(response, result["refresh_token"])
        
        # Revoke the old refresh token
        logout_token(old_jti)
        
        return response, status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 401

@auth_bp.route("/verify-email", methods=["GET"])
def verify_email():
    token = request.args.get("token")
    if not token:
        return jsonify(error_response("VALIDATION_ERROR", "Verification token is required")), 400
    
    from ..services.auth_service import verify_email_service
    try:
        result, status = verify_email_service(token)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 400
    except Exception as e:
        return jsonify(error_response("INTERNAL_ERROR", str(e))), 500

@auth_bp.route("/logout", methods=["POST"])
@jwt_required(optional=True)
def logout():
    response = jsonify(success_response({"message": "Logged out successfully"}))
    unset_jwt_cookies(response)
    
    # Revoke current token if it exists
    try:
        jwt_data = get_jwt()
        if jwt_data:
            logout_token(jwt_data["jti"])
    except:
        pass
        
    return response, 200