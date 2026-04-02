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
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "lostnfound.db")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024 # 50MB limit for large photos

    # JWT Configuration (Hardened for Production)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    JWT_ALGORITHM = "HS256"
    
    # Token Storage (RTR - Refresh Token Rotation)
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_REFRESH_COOKIE_NAME = "refresh_token_cookie"
    JWT_COOKIE_SECURE = False # MUST BE TRUE IN PROD (using False for dev testing)
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = "Strict"
    JWT_COOKIE_CSRF_PROTECT = False
    
    # Restrict Refresh Token to refresh endpoint
    JWT_REFRESH_COOKIE_PATH = "/api/auth/refresh"