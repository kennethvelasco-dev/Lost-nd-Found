from datetime import datetime, timezone
from .audit import log_action
from .items import get_found_item_by_id, get_published_found_items
from backend.services.scoring_service import compute_claim_score
from .base import get_db_connection
from .validators import (
    ValidationError,
    require_fields,
    validate_int,
    validate_found_item_id,
    validate_claim_decision
)
import json

# CREATE CLAIM
def create_claim(data):
    """Create a claim with score computation and validation. found_item_id is optional."""
    try:
        found_item_id = data.get("found_item_id")
        found_item = None
        score = 0

        if found_item_id:
            validate_found_item_id(found_item_id)
            found_item = get_found_item_by_id(found_item_id)
            if not found_item:
                return {"error": "Found item not found"}, 404
            
            # Compute score if linked to an item
            score_result = compute_claim_score(data, found_item)
            score = score_result.get("total", 0)

        fields = [
            "user_id", "found_item_id", "claimant_name", "claimant_email", 
            "answers", "verification_score", "decision", "created_at"
        ]
        placeholders = ["?", "?", "?", "?", "?", "?", "?", "?"]
        
        values = [
            data.get("user_id"),
            found_item_id,
            data.get("claimant_name", "Unknown"),
            data.get("claimant_email", "unknown@test.com"),
            data.get("answers", "{}") if isinstance(data.get("answers"), str) else json.dumps(data.get("answers", {})),
            score,
            "pending",
            datetime.now(timezone.utc).isoformat()
        ]

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = f"INSERT INTO claims ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, values)
            claim_id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

        log_action("create", "claim", claim_id, str(data.get("user_id", "system")))

        return {
            "message": "Claim submitted successfully", 
            "score": score,
            "claim_id": claim_id
        }, 201

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500

# LINK CLAIM
def link_claim_to_found_item(claim_id, found_item_id):
    """Links a general claim/report to a specific found item and updates score."""
    try:
        validate_int(claim_id, "claim_id")
        validate_found_item_id(found_item_id)

        found_item = get_found_item_by_id(found_item_id)
        if not found_item:
            return {"error": "Found item not found"}, 404

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            claim_row = cursor.execute("SELECT answers FROM claims WHERE id = ?", (claim_id,)).fetchone()
            if not claim_row:
                return {"error": "Claim not found"}, 404
            
            answers_json = claim_row["answers"]
            try:
                answers = json.loads(answers_json)
            except:
                answers = answers_json

            score_result = compute_claim_score(answers, found_item)
            score = score_result.get("total", 0)

            cursor.execute("""
                UPDATE claims 
                SET found_item_id = ?, verification_score = ? 
                WHERE id = ?
            """, (found_item_id, score, claim_id))
            conn.commit()
        finally:
            conn.close()

        log_action("link", "claim", claim_id, "system")
        return {"message": "Claim linked successfully", "score": score}, 200

    except Exception as e:
        return {"error": str(e)}, 500

# GET PENDING CLAIMS
def get_pending_claims():
    """Return all pending claims. Handles both linked and unlinked."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                c.id AS claim_id,
                c.user_id,
                c.found_item_id,
                c.claimant_name,
                c.claimant_email,
                c.answers,
                c.verification_score AS score,
                c.decision AS status,
                c.pickup_datetime,
                c.pickup_location,
                c.created_at,

                f.category AS found_category,
                f.item_type AS found_item_type,
                f.found_location
            FROM claims c
            LEFT JOIN found_items f ON c.found_item_id = f.id
            WHERE c.decision IN ('pending', 'approved')
            ORDER BY c.verification_score DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

# GET COMPLETED CLAIMS (For Reporting)
def get_completed_claims():
    """Return all completed claims for transaction reporting."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                c.id AS claim_id,
                c.user_id,
                c.found_item_id,
                c.claimant_name,
                c.claimant_email,
                c.verification_score AS score,
                c.decision AS status,
                c.pickup_datetime,
                c.pickup_location,
                c.handover_notes,
                c.completed_at,
                c.created_at,

                f.report_id AS found_report_id,
                f.category AS found_category,
                f.item_type AS found_item_type,
                f.found_location,
                f.found_datetime
            FROM claims c
            JOIN found_items f ON c.found_item_id = f.id
            WHERE c.decision = 'completed'
            ORDER BY c.completed_at DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

# UPDATE CLAIM STATUS
def update_claim_status(claim_id, new_status):
    """Update status of a claim with validation."""
    try:
        validate_int(claim_id, "claim_id")

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM claims WHERE id = ?", (claim_id,))
            if not cursor.fetchone():
                return {"error": "Claim not found"}, 404

            cursor.execute("UPDATE claims SET decision = ? WHERE id = ?", (new_status, claim_id))
            conn.commit()
        finally:
            conn.close()

        log_action("update_status", "claim", claim_id, "system")
        return {"message": "Claim status updated"}, 200

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code

# UPDATE CLAIM
def update_claim(claim_id, data):
    """Update claim fields with validation."""
    try:
        validate_int(claim_id, "claim_id")

        ALLOWED_FIELDS = {
            "claimant_name",
            "claimant_email",
            "answers",
            "decision"
        }

        updates = []
        values = []

        for key, value in data.items():
            if key in ALLOWED_FIELDS:
                updates.append(f"{key} = ?")
                if key == "answers" and not isinstance(value, str):
                    values.append(json.dumps(value))
                else:
                    values.append(value)

        if not updates:
            return {"error": "No valid fields to update"}, 400

        values.append(claim_id)

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = f"UPDATE claims SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        finally:
            conn.close()

        log_action("update", "claim", claim_id, "system")
        return {"message": "Claim updated successfully"}, 200

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code

# VERIFY CLAIM
def verify_claim(claim_id, decision, admin_username, handover_notes=None):
    """Approve, reject or complete a claim."""
    try:
        validate_int(claim_id, "claim_id")
        validate_claim_decision(decision)

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            row = cursor.execute("SELECT found_item_id, decision FROM claims WHERE id = ?", (claim_id,)).fetchone()
            if not row:
                return {"error": "Claim not found"}, 404
            
            current_decision = row["decision"]
            found_item_id = row["found_item_id"]

            if decision == "approved":
                # Ensure no OTHER claim is already approved/completed for this item
                if found_item_id:
                    other_approved = cursor.execute(
                        "SELECT id FROM claims WHERE found_item_id = ? AND decision IN ('approved', 'completed') AND id != ?",
                        (found_item_id, claim_id)
                    ).fetchone()
                    if other_approved:
                        return {"error": "Another claim is already approved or completed for this item"}, 400

            if decision == "completed":
                if current_decision != "approved":
                    return {"error": "Only approved claims can be completed"}, 400
                if not found_item_id:
                    return {"error": "Cannot complete a claim that is not linked to an item"}, 400
                
                # Perform completion
                completed_at = datetime.now(timezone.utc).isoformat()
                cursor.execute("""
                    UPDATE claims 
                    SET decision = ?, handover_notes = ?, completed_at = ? 
                    WHERE id = ?
                """, (decision, handover_notes, completed_at, claim_id))
                
                cursor.execute("UPDATE found_items SET status = 'returned' WHERE id = ?", (found_item_id,))
            else:
                if current_decision not in ("pending", "approved"):
                    return {"error": f"Claim already processed (Current status: {current_decision})"}, 400
                cursor.execute("UPDATE claims SET decision = ? WHERE id = ?", (decision, claim_id))
            
            conn.commit()
        finally:
            conn.close()

        log_action(decision, "claim", claim_id, admin_username, notes=handover_notes)
        return {"message": f"Claim {decision} successfully"}, 200

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500

# SCHEDULE PICKUP
def schedule_pickup(claim_id, pickup_datetime, pickup_location):
    """Sets scheduling info for an approved claim."""
    try:
        validate_int(claim_id, "claim_id")
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            row = cursor.execute("SELECT decision FROM claims WHERE id = ?", (claim_id,)).fetchone()
            if not row:
                return {"error": "Claim not found"}, 404
            
            if row["decision"] != "approved":
                return {"error": "Scheduling only allowed for approved claims"}, 400

            cursor.execute("""
                UPDATE claims 
                SET pickup_datetime = ?, pickup_location = ?
                WHERE id = ?
            """, (pickup_datetime, pickup_location, claim_id))
            conn.commit()
        finally:
            conn.close()

        log_action("schedule", "claim", claim_id, "system")
        return {"message": "Pickup scheduled successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_claim_by_id(claim_id):
    """Helper to fetch a claim full record."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        row = cursor.execute("SELECT * FROM claims WHERE id = ?", (claim_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
