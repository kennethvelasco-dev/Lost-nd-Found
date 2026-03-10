from flask import Flask, request
from flask_jwt_extended import JWTManager

from backend.config.config import Config
from backend.routes.auth_routes import auth_bp
from backend.routes.item_routes import item_bp
from backend.routes.claim_routes import claim_bp
from backend.routes.admin_routes import admin_bp
from backend.models import init_db
from backend.helpers.user_helpers import create_default_admin
from backend.helpers.response import error_response
from flask import jsonify
from werkzeug.exceptions import HTTPException

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(item_bp, url_prefix="/api/items")
    app.register_blueprint(claim_bp, url_prefix="/api/claims")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    

    @app.errorhandler(Exception)
    def handle_exception(e):
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
