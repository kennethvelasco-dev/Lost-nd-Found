import sqlite3
import json

def check_users():
    conn = sqlite3.connect('backend/lostnfound.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    
    users = []
    for row in rows:
        users.append(dict(row))
        
    print(json.dumps(users, indent=2))
    conn.close()

if __name__ == "__main__":
    check_users()
