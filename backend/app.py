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
    return is_token_revoked(jti)  # True if revoked, False if valid

# Callback response for revoked tokens
@jwt.revoked_token_loader
def revoked_token_response(jwt_header, jwt_payload):
    return jsonify({"error": "Token has been revoked"}), 401

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
