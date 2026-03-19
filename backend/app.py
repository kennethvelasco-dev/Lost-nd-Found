import sys
import os

# Ensure the project root is in sys.path for robust module resolution
# This allows running the app from either the root or inside 'backend/'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend import create_app

from flask import jsonify
from backend.services.auth_service import is_token_revoked
from backend.extensions import jwt

app = create_app()

# Callback to check if token is revoked
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload.get("jti")
    return is_token_revoked(jti)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"DEBUG: Token expired. Payload: {jwt_payload}")
    return jsonify({"error": "The token has expired", "sub_status": "TOKEN_EXPIRED"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"DEBUG: Invalid token provided. Error: {error}")
    return jsonify({"error": "Signature verification failed", "sub_status": "TOKEN_INVALID"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"DEBUG: Missing Authorization Header. Error: {error}")
    return jsonify({"error": "Request does not contain an access token", "sub_status": "TOKEN_MISSING"}), 401

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """Global handler for catching all unhandled exceptions."""
    import traceback
    # Log detailed error for developers
    print(f"CRITICAL ERROR: {str(e)}\n{traceback.format_exc()}")
    # Return friendly error to users
    return jsonify({
        "success": False,
        "message": "A critical server error occurred. Please try again later.",
        "error_code": "INTERNAL_SERVER_ERROR"
    }), 500

@jwt.revoked_token_loader
def revoked_token_response(jwt_header, jwt_payload):
    print(f"DEBUG: Token revoked. JTI: {jwt_payload.get('jti')}")
    return jsonify({"error": "Token has been revoked", "sub_status": "TOKEN_REVOKED"}), 401

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
