from flask import Blueprint, jsonify
from backend.models.base import get_db_connection

health_bp = Blueprint("health", __name__)

@health_bp.route("/status", methods=["GET"])
def health_check():
    """
    Health check endpoint for monitoring systems.
    Verifies database connectivity.
    """
    health_status = {
        "status": "healthy",
        "services": {
            "api": "up",
            "database": "down"
        }
    }
    
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        health_status["services"]["database"] = "up"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["error"] = str(e)

    return jsonify(health_status), 200 if health_status["status"] == "healthy" else 503
