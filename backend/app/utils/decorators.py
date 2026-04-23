from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps
from .response import error_response


def admin_required(fn):
    """
    Decorator to ensure the current user has an 'admin' role.
    Verifies JWT in request and checks the 'role' claim.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Ensure a valid JWT exists first
            verify_jwt_in_request()
            claims = get_jwt()
        except Exception:
            return (
                jsonify(error_response("UNAUTHORIZED", "Invalid or missing token")),
                401,
            )

        if claims.get("role") != "admin":
            return jsonify(error_response("FORBIDDEN", "Admin access required")), 403

        return fn(*args, **kwargs)

    return wrapper
