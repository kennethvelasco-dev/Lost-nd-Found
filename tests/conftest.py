import os
import pytest
import sqlite3
import tempfile
from backend.app import create_app
from backend.app.models import init_db


@pytest.fixture
def app(tmp_path):
    # Create a temporary directory and file for the database
    d = tmp_path / "testdata"
    d.mkdir()
    db_path = d / "test.db"

    app = create_app()
    app.config.update({"TESTING": True, "DATABASE_PATH": str(db_path)})

    with app.app_context():
        init_db()
        yield app

    # tmp_path is automatically cleaned up by pytest


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    path = app.config["DATABASE_PATH"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
