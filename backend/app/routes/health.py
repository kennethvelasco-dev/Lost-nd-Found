from flask import Blueprint, jsonify
from ..models.base import get_db_connection

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
    
    conn = None # Initialize conn to None
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        health_status["services"]["database"] = "up"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["error"] = str(e)
    finally:
        if conn: # Ensure conn exists before trying to close it
            conn.close()

    return jsonify(health_status), 200 if health_status["status"] == "healthy" else 503
