from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import jwt, limiter
from .config.config import Config
from .models import init_db
from .utils.response import error_response
from .services.auth_service import is_token_revoked
from werkzeug.exceptions import HTTPException

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    CORS(app, supports_credentials=True, origins=app.config.get("CORS_ORIGINS", "*"))
    jwt.init_app(app)
    limiter.init_app(app)

    # JWT Callbacks
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        return is_token_revoked(jti)

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
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return jsonify(error_response("HTTP_ERROR", e.description)), e.code
        
        import traceback
        print(f"CRITICAL ERROR: {str(e)}\n{traceback.format_exc()}")
        return jsonify(error_response("INTERNAL_SERVER_ERROR", "An unexpected server error occurred.")), 500

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
