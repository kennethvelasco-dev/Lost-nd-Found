import os
from datetime import timedelta


class Config:
    """
    Base configuration.
    Used for development unless overridden.
    """

    # Core Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    TESTING = False
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "database.db")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024 # 50MB limit for large photos

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")

    # Explicit token behavior (Longer for dev stability)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    JWT_ALGORITHM = "HS256"

    # Safer defaults
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"