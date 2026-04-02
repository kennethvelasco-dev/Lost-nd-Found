import sqlite3
import json

conn = sqlite3.connect('models/database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

result = {}

cursor.execute("SELECT id, report_id, status, recipient_name, recipient_id, resolved_at FROM found_items")
result["found_items"] = [dict(r) for r in cursor.fetchall()]

cursor.execute("SELECT id, report_id, status, recipient_name, recipient_id, resolved_at FROM lost_items")
result["lost_items"] = [dict(r) for r in cursor.fetchall()]

cursor.execute("SELECT id, found_item_id, lost_item_id, decision, handover_notes, completed_at FROM claims")
result["claims"] = [dict(r) for r in cursor.fetchall()]

with open("check_db_clean.json", "w") as f:
    json.dump(result, f, indent=2)

print("Dumped to check_db_clean.json")
conn.close()
