from datetime import datetime, timezone
from .audit import log_action
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
        lost_item_id = None
        found_item = None
        score = 0

        if found_item_id is not None:
            validate_found_item_id(found_item_id)
            from .items import get_item_universal_db
            found_item = get_item_universal_db(found_item_id)
            
            if not found_item:
                return {"error": f"Item with ID {found_item_id} not found in directory"}, 404
            
            # Map the ID to the correct column based on its actual table
            if found_item.get("type") == "lost":
                lost_item_id = found_item_id
                found_item_id = None 
            
            # Compute score if linked to an item
            from ..services.scoring_service import compute_claim_score
            score_result = compute_claim_score(data.get("answers", {}), found_item)
            score = score_result.get("total", 0)

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Check for existing pending claim for this user and item
            existing = None
            if found_item_id:
                existing = cursor.execute(
                    "SELECT id FROM claims WHERE user_id = ? AND found_item_id = ? AND decision = 'pending'",
                    (data.get("user_id"), found_item_id)
                ).fetchone()
            elif lost_item_id:
                existing = cursor.execute(
                    "SELECT id FROM claims WHERE user_id = ? AND lost_item_id = ? AND decision = 'pending'",
                    (data.get("user_id"), lost_item_id)
                ).fetchone()

            if existing:
                # UPDATE instead of INSERT
                claim_id = existing["id"]
                query = """
                    UPDATE claims 
                    SET answers = ?, verification_score = ?, created_at = ?
                    WHERE id = ?
                """
                cursor.execute(query, (
                    json.dumps(data.get("answers", {})),
                    score,
                    datetime.now(timezone.utc).isoformat(),
                    claim_id
                ))
                conn.commit()
                message = "Claim updated successfully"
                status_code = 200
            else:
                # INSERT new claim
                query = """
                    INSERT INTO claims (
                        user_id, found_item_id, lost_item_id, claimant_name, claimant_email, 
                        lost_location, lost_datetime,
                        answers, verification_score, decision, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = [
                    data.get("user_id"),
                    found_item_id,
                    lost_item_id,
                    data.get("claimant_name", "Unknown"),
                    data.get("claimant_email", "unknown@test.com"),
                    data.get("lost_location"),
                    data.get("lost_datetime"),
                    json.dumps(data.get("answers", {})),
                    score,
                    "pending",
                    datetime.now(timezone.utc).isoformat()
                ]
                cursor.execute(query, values)
                claim_id = cursor.lastrowid
                conn.commit()
                message = "Claim submitted successfully"
                status_code = 201
        finally:
            conn.close()

        log_action("save", "claim", claim_id, str(data.get("user_id", "system")))

        return {
            "message": message, 
            "score": score,
            "claim_id": claim_id
        }, status_code

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code

    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR in create_claim: {str(e)}\n{traceback.format_exc()}")
        return {"error": f"Internal server error while creating claim: {str(e)}"}, 500

# LINK CLAIM
def link_claim_to_found_item(claim_id, found_item_id):
    """Links a general claim/report to a specific found item and updates score."""
    try:
        validate_int(claim_id, "claim_id")
        validate_found_item_id(found_item_id)

        from .items import get_item_universal_db
        found_item = get_item_universal_db(found_item_id)
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

            from ..services.scoring_service import compute_claim_score
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
def get_filtered_claims_db(status_filter=['pending']):
    """Return claims filtered by status. Handles both linked and unlinked."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        placeholders = ', '.join(['?'] * len(status_filter))
        query = f"""
            SELECT
                c.id AS claim_id,
                c.id, 
                c.user_id,
                u.username AS user_name,
                c.claimant_name,
                c.claimant_email,
                c.answers,
                c.verification_score AS score,
                c.decision AS status,
                c.pickup_datetime,
                c.pickup_location,
                c.created_at,
                COALESCE(f.id, l.id) AS item_id,
                f.id AS found_item_id,
                l.id AS lost_item_id,

                COALESCE(f.category, l.category) AS category,
                COALESCE(f.item_type, l.item_type) AS item_type,
                COALESCE(f.found_location, l.last_seen_location) AS location,
                COALESCE(f.main_picture, l.main_picture) AS main_picture,
                COALESCE(f.color, l.color) AS item_color,
                COALESCE(f.brand, l.brand) AS item_brand,
                l.last_seen_datetime AS lost_date,
                f.found_datetime AS found_date,
                COALESCE(f.found_datetime, l.last_seen_datetime) AS incident_date,
                COALESCE(f.created_at, l.created_at) AS item_reported_at
            FROM claims c
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN found_items f ON c.found_item_id = f.id
            LEFT JOIN lost_items l ON c.lost_item_id = l.id
            WHERE c.decision IN ({placeholders})
            ORDER BY c.verification_score DESC
        """
        cursor.execute(query, status_filter)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            if d.get("answers"):
                try:
                    d["answers"] = json.loads(d["answers"])
                except:
                    pass
            result.append(d)
        return result
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
                u.username AS user_name,
                c.claimant_name,
                c.claimant_email,
                c.verification_score AS score,
                c.decision AS status,
                c.pickup_datetime,
                c.pickup_location,
                c.handover_notes,
                c.completed_at,
                c.created_at,

                COALESCE(f.category, l.category) AS category,
                COALESCE(f.item_type, l.item_type) AS item_type,
                COALESCE(f.found_location, l.last_seen_location) AS location,
                COALESCE(f.color, l.color) AS item_color,
                COALESCE(f.brand, l.brand) AS item_brand,
                COALESCE(f.found_datetime, l.last_seen_datetime) AS incident_date,
                COALESCE(f.created_at, l.created_at) AS item_reported_at
            FROM claims c
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN found_items f ON c.found_item_id = f.id
            LEFT JOIN lost_items l ON c.lost_item_id = l.id
            WHERE c.decision = 'completed'
            ORDER BY c.completed_at DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            if d.get("answers"):
                try:
                    d["answers"] = json.loads(d["answers"])
                except:
                    pass
            result.append(d)
        return result
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
            row = cursor.execute(
                "SELECT found_item_id, lost_item_id, decision FROM claims WHERE id = ?", 
                (claim_id,)
            ).fetchone()
            
            if not row:
                return {"error": "Claim not found"}, 404
            
            current_decision = row["decision"]
            found_item_id = row["found_item_id"]
            lost_item_id = row["lost_item_id"]

            if decision == "approved":
                # Ensure no OTHER claim is already approved/completed for this specific item
                if found_item_id:
                    other_approved = cursor.execute(
                        "SELECT id FROM claims WHERE found_item_id = ? AND decision IN ('approved', 'completed') AND id != ?",
                        (found_item_id, claim_id)
                    ).fetchone()
                    if other_approved:
                        return {"error": "Another claim is already approved or completed for this found report"}, 400
                elif lost_item_id:
                    other_approved = cursor.execute(
                        "SELECT id FROM claims WHERE lost_item_id = ? AND decision IN ('approved', 'completed') AND id != ?",
                        (lost_item_id, claim_id)
                    ).fetchone()
                    if other_approved:
                        return {"error": "Another claim is already approved or completed for this lost report"}, 400

            if decision == "completed":
                if current_decision != "approved":
                    return {"error": "Only approved claims can be completed"}, 400
                
                if not found_item_id and not lost_item_id:
                    return {"error": "Cannot complete a claim that is not linked to any item"}, 400
                
                # Perform completion
                completed_at = datetime.now(timezone.utc).isoformat()
                cursor.execute("""
                    UPDATE claims 
                    SET decision = ?, handover_notes = ?, completed_at = ? 
                    WHERE id = ?
                """, (decision, handover_notes, completed_at, claim_id))
                
                # Update the correct item table status to 'found' (Resolved)
                if found_item_id:
                    cursor.execute("UPDATE found_items SET status = 'found' WHERE id = ?", (found_item_id,))
                elif lost_item_id:
                    cursor.execute("UPDATE lost_items SET status = 'found' WHERE id = ?", (lost_item_id,))
            else:
                # Basic Approve/Reject for pending/approved claims
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

def get_claim_detail_db(claim_id):
    """Fetch a single claim with full joined report and user info."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT
                c.id AS claim_id,
                c.id, 
                c.user_id,
                u.username AS user_name,
                c.claimant_name,
                c.claimant_email,
                c.answers,
                c.verification_score AS score,
                c.decision AS status,
                c.pickup_datetime,
                c.pickup_location,
                c.created_at,
                c.handover_notes,
                c.completed_at,

                COALESCE(f.id, l.id) AS item_id,
                c.found_item_id,
                c.lost_item_id,
                COALESCE(f.category, l.category) AS category,
                COALESCE(f.item_type, l.item_type) AS item_type,
                COALESCE(f.found_location, l.last_seen_location) AS location,
                COALESCE(f.main_picture, l.main_picture) AS main_picture,
                COALESCE(f.color, l.color) AS item_color,
                COALESCE(f.brand, l.brand) AS item_brand,
                l.last_seen_datetime AS lost_date,
                f.found_datetime AS found_date,
                COALESCE(f.found_datetime, l.last_seen_datetime) AS incident_date,
                COALESCE(f.public_description, l.public_description) AS item_description,
                COALESCE(f.created_at, l.created_at) AS item_reported_at
            FROM claims c
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN found_items f ON c.found_item_id = f.id
            LEFT JOIN lost_items l ON c.lost_item_id = l.id
            WHERE c.id = ?
        """
        row = cursor.execute(query, (claim_id,)).fetchone()
        if not row:
            return None
        
        d = dict(row)
        if d.get("answers"):
            try:
                d["answers"] = json.loads(d["answers"])
            except:
                pass
        return d
    finally:
        conn.close()

def get_user_claims_db(user_id):
    """Get all non-dismissed claims for a specific user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT c.*, c.id AS claim_id, c.decision AS status,
                   u.username AS user_name,
                   COALESCE(f.item_type, l.item_type) AS item_type,
                   COALESCE(f.category, l.category) AS category,
                   COALESCE(f.color, l.color) AS item_color,
                   COALESCE(f.brand, l.brand) AS item_brand,
                   COALESCE(f.found_datetime, l.last_seen_datetime) AS incident_date,
                   COALESCE(f.created_at, l.created_at) AS item_reported_at
            FROM claims c
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN found_items f ON c.found_item_id = f.id
            LEFT JOIN lost_items l ON c.lost_item_id = l.id
            WHERE c.user_id = ? AND c.is_dismissed = 0
            ORDER BY c.created_at DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            if d.get("answers"):
                try:
                    d["answers"] = json.loads(d["answers"])
                except:
                    pass
            result.append(d)
        return result
    finally:
        conn.close()

def dismiss_claim_db(claim_id, user_id):
    """Mark a claim as dismissed for the user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE claims SET is_dismissed = 1 WHERE id = ? AND user_id = ?", (claim_id, user_id))
        conn.commit()
        return {"message": "Claim dismissed successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        conn.close()
