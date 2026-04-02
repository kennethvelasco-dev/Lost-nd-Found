import sqlite3
import os

from flask import current_app

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "..", "lostnfound.db")

def get_db_path():
    if current_app:
        return current_app.config.get("DATABASE_PATH", DEFAULT_DB)
    return DEFAULT_DB

def get_db_connection():
    path = get_db_path()
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cursor.executescript(schema_sql)

        conn.commit()
    finally:
        conn.close()
