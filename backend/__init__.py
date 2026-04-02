from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from backend.config.config import Config
from backend.models import init_db
from backend.helpers.user_helpers import create_default_admin
from backend.helpers.response import error_response
from flask import jsonify
from werkzeug.exceptions import HTTPException

from backend.extensions import jwt, limiter

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(Config)

    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from backend.services.auth_service import is_token_revoked
        return is_token_revoked(jwt_payload["jti"])
    
    if app.config.get("TESTING"):
        limiter.enabled = False
    
    limiter.init_app(app)

    # Deferred imports to avoid circular dependency with limiter
    from backend.routes.auth_routes import auth_bp
    from backend.routes.item_routes import item_bp
    from backend.routes.claim_routes import claim_bp
    from backend.routes.admin_routes import admin_bp
    from backend.routes.health import health_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(item_bp, url_prefix="/api/items")
    app.register_blueprint(claim_bp, url_prefix="/api/claims")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(health_bp, url_prefix="/api")
    
    @app.after_request
    def add_security_headers(response):
        """Inject mandatory security headers into every response."""
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; object-src 'none';"
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        if app.config.get("TESTING"):
            raise e
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return jsonify(error_response("HTTP_ERROR", e.description)), e.code
        
        # Log the internal error (using app.logger or print for now)
        app.logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
        
        # Return a safe, standardized error response
        return jsonify(error_response("INTERNAL_SERVER_ERROR", "An unexpected server error occurred. Please contact support.")), 500

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify(error_response("NOT_FOUND", "The requested resource was not found.")), 404

    @app.errorhandler(400)
    def handle_400(e):
        return jsonify(error_response("BAD_REQUEST", "Bad request.")), 400

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify(error_response("INTERNAL_SERVER_ERROR", "Internal server error.")), 500

    with app.app_context():
        init_db()
        create_default_admin()

    return app
