import os
import pytest
import sqlite3
import tempfile
from backend.app import create_app
from backend.app.models import init_db


@pytest.fixture
def app(tmp_path):
    # Create a temporary file for the database to avoid :memory: sharing issues in some cases
    db_fd, db_path = tempfile.mkstemp()

    app = create_app("testing")
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}"
    })

    with app.app_context():
        init_db()
        yield app

    os.close(db_fd)
    os.unlink(db_path)

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
