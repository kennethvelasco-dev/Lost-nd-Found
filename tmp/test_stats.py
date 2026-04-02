import sqlite3

def test_stats():
    conn = sqlite3.connect('backend/lostnfound.db')
    cursor = conn.cursor()
    try:
        print("Checking lost_items...")
        cursor.execute("SELECT COUNT(*) FROM lost_items WHERE status = 'lost'")
        print(f"Lost: {cursor.fetchone()[0]}")
        
        print("Checking found_items...")
        cursor.execute("SELECT COUNT(*) FROM found_items WHERE status = 'found'")
        print(f"Found: {cursor.fetchone()[0]}")
        
        print("Checking claims...")
        cursor.execute("SELECT COUNT(*) FROM claims WHERE decision = 'pending'")
        print(f"Claims: {cursor.fetchone()[0]}")
        
        print("Checking resolved...")
        cursor.execute("SELECT COUNT(*) FROM found_items WHERE status = 'returned'")
        res = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM lost_items WHERE status = 'returned'")
        res += cursor.fetchone()[0]
        print(f"Resolved: {res}")
        
        print("Success!")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    test_stats()
