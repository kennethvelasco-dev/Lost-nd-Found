from functools import wraps
from flask import request, jsonify
from .response import error_response


def require_json_fields(required_fields):
    """
    Decorator to enforce presence of JSON fields in POST/PUT requests.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify(error_response("BAD_REQUEST", "JSON body required")), 400

            data = request.get_json()
            missing = [field for field in required_fields if field not in data]

            if missing:
                return (
                    jsonify(
                        error_response(
                            "VALIDATION_ERROR",
                            f"Missing required fields: {', '.join(missing)}",
                        )
                    ),
                    400,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def sanitize_input(val):
    """Basic string sanitization."""
    if isinstance(val, str):
        return val.strip()
    return val
