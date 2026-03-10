from backend.__init__ import create_app
from flask import jsonify
from backend.services.auth_service import is_token_revoked
from backend.extensions import jwt

app = create_app()

# Callback to check if token is revoked
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload.get("jti")
    return is_token_revoked(jti)  # True if revoked, False if valid

# Callback response for revoked tokens
@jwt.revoked_token_loader
def revoked_token_response(jwt_header, jwt_payload):
    return jsonify({"error": "Token has been revoked"}), 401

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
