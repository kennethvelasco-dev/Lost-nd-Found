import os
import logging
from flask import current_app
from sqlalchemy import text
from ..extensions import db

logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Legacy wrapper for raw db connection if needed.
    In SQLAlchemy context, we usually use db.session.
    """
    return db.engine.raw_connection()


def init_db():
    """Initialized the database by executing the schema script."""
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "migrations", "schema.sql"
    )

    if not os.path.exists(schema_path):
        logger.error(f"Schema file not found at {schema_path}")
        return

    with open(schema_path, "r") as f:
        schema_sql = f.read()

    try:
        # Split by semicolon for Postgres compatibility if not using executescript
        # SQLite's executescript is convenient, but for Postgres we need individual statements
        # or we use the underlying driver's capabilities.
        with current_app.app_context():
            # For simplicity in this refactor, we'll execute the script in blocks
            # separated by double-newlines or semicolons if they aren't in strings.
            # A better way for production is real migrations (Alembic).
            statements = schema_sql.split(";")
            for statement in statements:
                if statement.strip():
                    db.session.execute(text(statement))
            db.session.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to initialize database: {str(e)}")
        raise e
