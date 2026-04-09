from app.models.base import get_db_connection

def get_claim_by_id(claim_id: int):
    """Fetch a claim by ID. Returns dict or None if not found."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM claims WHERE id=?", (claim_id,))
        row = cursor.fetchone()

        if not row:
            return None

        keys = [column[0] for column in cursor.description]
        claim = dict(zip(keys, row))
        return claim
    finally:
        conn.close()