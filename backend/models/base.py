import sqlite3
import os

DataBase = os.path.join(os.path.dirname(__file__), "database.db")

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DataBase)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)

    conn.commit()
    conn.close()

