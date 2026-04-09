from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_identity, 
    get_jwt, 
    set_access_cookies, 
    set_refresh_cookies, 
    unset_jwt_cookies
)
from ..services.auth_service import (
    register_user, 
    login_user, 
    refresh_token_service, 
    logout_token,
    request_password_reset,
    reset_password,
    verify_email_service
)
from ..utils.response import success_response, error_response
from ..models import ValidationError
from ..extensions import limiter
from ..utils.production_safety import require_json_fields

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("3 per 15 minutes")
@require_json_fields(["username", "password", "role", "email"])
def register():
    data = request.get_json() or {}
    try:
        result, status = register_user(data)
        # MUST-FIX: Returns JSON: { "message": ... }
        return jsonify({"message": result["message"]}), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 400

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per 15 minutes")
@require_json_fields(["username", "password"])
def login():
    data = request.get_json() or {}
    try:
        result, status = login_user(data)
        # MUST-FIX: Returns JSON: { "data": { "access_token": "..." } }
        response = jsonify(success_response(data={
            "access_token": result["access_token"],
            "user": result["user"]
        }, message=result["message"]))
        
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
        claims = get_jwt()
        role = claims.get("role")
        auth_time = claims.get("auth_time")
        old_jti = claims["jti"]
        
        # RTR: Generate new tokens with preservation of auth_time
        result, status = refresh_token_service(user_id, role, auth_time)
        
        response = jsonify(success_response({"message": "Token refreshed"}))
        set_access_cookies(response, result["access_token"])
        set_refresh_cookies(response, result["refresh_token"])
        
        # Revoke the old refresh token
        logout_token(old_jti)
        
        return response, status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 401

@auth_bp.route("/verify-email", methods=["GET"])
@limiter.limit("5 per minute")
def verify_email():
    token = request.args.get("token")
    if not token:
        return jsonify(error_response("VALIDATION_ERROR", "Verification token is required")), 400
    
    try:
        result, status = verify_email_service(token)
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 400
    except Exception as e:
        return jsonify(error_response("INTERNAL_ERROR", str(e))), 500

@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("3 per hour")
@require_json_fields(["email"])
def forgot_password():
    data = request.get_json()
    result, status = request_password_reset(data["email"])
    return jsonify(success_response(result)), status

@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("5 per hour")
@require_json_fields(["token", "new_password"])
def reset_password_route():
    data = request.get_json()
    try:
        result, status = reset_password(data["token"], data["new_password"])
        return jsonify(success_response(result)), status
    except ValidationError as ve:
        return jsonify(error_response("VALIDATION_ERROR", ve.message)), 400

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