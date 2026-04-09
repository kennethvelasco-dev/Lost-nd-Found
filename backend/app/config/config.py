import os
from datetime import timedelta

class Config:
    """
    Base configuration.
    Used for development unless overridden by environment variables.
    """

    # Core Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    TESTING = os.environ.get("FLASK_TESTING", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "lostnfound.db"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024))

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINS", 15)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS", 7)))
    
    JWT_ALGORITHM = "HS256"
    
    # Token Storage
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_REFRESH_COOKIE_NAME = "refresh_token_cookie"
    
    # Security Flags (Should be True in Production with HTTPS)
    JWT_COOKIE_SECURE = os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_HTTPONLY = os.environ.get("JWT_COOKIE_HTTPONLY", "true").lower() == "true"
    JWT_COOKIE_SAMESITE = os.environ.get("JWT_COOKIE_SAMESITE", "Strict")
    JWT_COOKIE_CSRF_PROTECT = os.environ.get("JWT_COOKIE_CSRF_PROTECT", "false").lower() == "true"
    
    # Restrict Refresh Token to refresh endpoint
    JWT_REFRESH_COOKIE_PATH = "/api/auth/refresh"

    # CORS Configuration
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # Password Reset
    RESET_TOKEN_EXPIRY_MINUTES = int(os.environ.get("RESET_TOKEN_EXPIRY_MINUTES", 60))