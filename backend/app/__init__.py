import os
import time
from flask import Flask, jsonify, json
from flask_cors import CORS
from .extensions import jwt, limiter, db
from .config.config import Config
from .models import init_db
from .models.validators import ValidationError
from .utils.response import error_response
from .services.auth_service import is_token_revoked
from werkzeug.exceptions import HTTPException

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    from .config.config import config_by_name
    config_class = config_by_name.get(config_name, config_by_name["default"])

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    CORS(app, supports_credentials=True, origins=app.config.get("CORS_ORIGINS", "*"))
    jwt.init_app(app)
    limiter.init_app(app)
    db.init_app(app)

    # JWT Callbacks
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        # 1. Check database blocklist
        jti = jwt_payload.get("jti")
        if is_token_revoked(jti):
            return True
            
        # 2. Check absolute timeout (24h)
        auth_time = jwt_payload.get("auth_time")
        if auth_time:
            max_age = app.config.get("SESSION_ABSOLUTE_TIMEOUT", 24) * 3600
            if time.time() - auth_time > max_age:
                return True # Treat as revoked/expired
                
        return False

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify(error_response("TOKEN_EXPIRED", "The token has expired")), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(error_response("TOKEN_INVALID", "Signature verification failed")), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify(error_response("TOKEN_MISSING", "Request does not contain an access token")), 401

    # Register Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.item_routes import item_bp
    from .routes.claim_routes import claim_bp
    from .routes.admin_routes import admin_bp
    from .routes.health import health_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(item_bp, url_prefix="/api/items")
    app.register_blueprint(claim_bp, url_prefix="/api/claims")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(health_bp, url_prefix="/api")

    # Global Error Handlers
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        status_code = getattr(e, "status_code", 400)
        return jsonify(error_response("VALIDATION_ERROR", str(e))), status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        response.data = json.dumps(error_response("HTTP_ERROR", e.description))
        response.content_type = "application/json"
        return response, e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the full error server-side
        import traceback
        app.logger.error(f"UNHANDLED EXCEPTION: {str(e)}\n{traceback.format_exc()}")
        
        # Determine status code
        status_code = 500
        if isinstance(e, HTTPException):
            status_code = e.code
            message = e.description
        else:
            message = "An unexpected server error occurred." if not app.debug else str(e)

        return jsonify(error_response("SERVER_ERROR", message)), status_code

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    with app.app_context():
        init_db()
        # Initialize default data if needed
        from .utils.user_helpers import create_default_admin
        create_default_admin()

    return app
