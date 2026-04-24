import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024))
    RESET_TOKEN_EXPIRY_MINUTES = int(os.environ.get("RESET_TOKEN_EXPIRY_MINUTES", 60))

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lostnfound.db'))}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_MINS", 15))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_DAYS", 7))
    )
    JWT_ALGORITHM = "HS256"

    # Token Storage
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_REFRESH_COOKIE_NAME = "refresh_token_cookie"

    # Security Flags (Should be True in Production)
    JWT_COOKIE_SECURE = os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_HTTPONLY = (
        os.environ.get("JWT_COOKIE_HTTPONLY", "true").lower() == "true"
    )
    JWT_COOKIE_SAMESITE = os.environ.get("JWT_COOKIE_SAMESITE", "Lax")
    JWT_COOKIE_CSRF_PROTECT = (
        os.environ.get("JWT_COOKIE_CSRF_PROTECT", "false").lower() == "true"
    )
    JWT_REFRESH_COOKIE_PATH = "/api/auth/refresh"

    # CORS Configuration
    raw_origins = os.environ.get("CORS_ORIGINS", "*")
    CORS_ORIGINS = (
        [o.strip() for o in raw_origins.split(",")] if raw_origins != "*" else "*"
    )

    # Email (SMTP)
    SMTP_SERVER = os.environ.get("SMTP_SERVER")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"
    SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "onboarding@yourdomain.com")

    # absolute timeout logic
    SESSION_ABSOLUTE_TIMEOUT = int(os.environ.get("SESSION_ABSOLUTE_TIMEOUT_HOURS", 24))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # Enforce secure cookies in production
    JWT_COOKIE_SECURE = True
    # Cross-site SPA (Vercel frontend) requires SameSite=None so cookies are sent
    JWT_COOKIE_SAMESITE = "None"


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Disable CSRF and other checks for tests if needed
    JWT_COOKIE_CSRF_PROTECT = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
