import json
import logging
from datetime import datetime, timezone
from sqlalchemy import text
from ..extensions import db
from .audit import log_action
from .validators import (
    ValidationError,
    validate_int,
    validate_found_item_id,
    validate_claim_decision,
)

logger = logging.getLogger(__name__)


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
                return {
                    "error": f"Item with ID {found_item_id} not found in directory"
                }, 404

            # Map the ID to the correct column based on its actual table
            if found_item.get("type") == "lost":
                lost_item_id = found_item_id
                found_item_id = None

            # Compute score if linked to an item
            from ..services.scoring_service import compute_claim_score

            score_result = compute_claim_score(data.get("answers", {}), found_item)
            score = score_result.get("total", 0)

        # Check for existing pending claim for this user and item
        existing = None
        if found_item_id:
            query = text(
                "SELECT id FROM claims WHERE user_id = :user_id AND found_item_id = :item_id AND decision = 'pending'"
            )
            existing = db.session.execute(
                query, {"user_id": data.get("user_id"), "item_id": found_item_id}
            ).fetchone()
        elif lost_item_id:
            query = text(
                "SELECT id FROM claims WHERE user_id = :user_id AND lost_item_id = :item_id AND decision = 'pending'"
            )
            existing = db.session.execute(
                query, {"user_id": data.get("user_id"), "item_id": lost_item_id}
            ).fetchone()

        if existing:
            # UPDATE instead of INSERT
            claim_id = existing.id
            update_query = text(
                """
                UPDATE claims 
                SET answers = :answers, verification_score = :score, created_at = :now
                WHERE id = :id
            """
            )
            db.session.execute(
                update_query,
                {
                    "answers": json.dumps(data.get("answers", {})),
                    "score": score,
                    "now": datetime.now(timezone.utc),
                    "id": claim_id,
                },
            )
            db.session.commit()
            message = "Claim updated successfully"
            status_code = 200
        else:
            # INSERT new claim
            insert_query = text(
                """
                INSERT INTO claims (
                    user_id, found_item_id, lost_item_id, claimant_name, claimant_email, 
                    lost_location, lost_datetime,
                    answers, verification_score, decision, created_at
                ) VALUES (:user_id, :found_item_id, :lost_item_id, :claimant_name, :claimant_email, 
                        :lost_location, :lost_datetime, :answers, :score, :decision, :now)
                RETURNING id
            """
            )
            params = {
                "user_id": data.get("user_id"),
                "found_item_id": found_item_id,
                "lost_item_id": lost_item_id,
                "claimant_name": data.get("claimant_name", "Unknown"),
                "claimant_email": data.get("claimant_email", "unknown@test.com"),
                "lost_location": data.get("lost_location"),
                "lost_datetime": data.get("lost_datetime"),
                "answers": json.dumps(data.get("answers", {})),
                "score": score,
                "decision": "pending",
                "now": datetime.now(timezone.utc),
            }
            result = db.session.execute(insert_query, params)
            row = result.fetchone()
            db.session.commit()
            claim_id = row[0] if row else None
            message = "Claim submitted successfully"
            status_code = 201

        log_action("save", "claim", claim_id, str(data.get("user_id", "system")))

        return {"message": message, "score": score, "claim_id": claim_id}, status_code

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code
    except Exception as e:
        import traceback

        logger.error(
            f"CRITICAL ERROR in create_claim: {str(e)}\n{traceback.format_exc()}"
        )
        return {"error": "Internal server error while creating claim."}, 500


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

        query = text("SELECT answers FROM claims WHERE id = :id")
        claim_row = db.session.execute(query, {"id": claim_id}).fetchone()
        if not claim_row:
            return {"error": "Claim not found"}, 404

        answers_json = claim_row.answers
        try:
            answers = (
                json.loads(answers_json)
                if isinstance(answers_json, str)
                else answers_json
            )
        except:
            answers = answers_json

        from ..services.scoring_service import compute_claim_score

        score_result = compute_claim_score(answers, found_item)
        score = score_result.get("total", 0)

        update_query = text(
            """
            UPDATE claims 
            SET found_item_id = :f_id, verification_score = :score 
            WHERE id = :id
        """
        )
        db.session.execute(
            update_query, {"f_id": found_item_id, "score": score, "id": claim_id}
        )
        db.session.commit()

        log_action("link", "claim", claim_id, "system")
        return {"message": "Claim linked successfully", "score": score}, 200

    except Exception as e:
        logger.error(f"Error linking claim: {str(e)}")
        return {"error": "Database error while linking"}, 500


# GET FILTERED CLAIMS
def get_filtered_claims_db(status_filter=["pending"]):
    """
    Return claims filtered by decision/status. Handles both linked and unlinked.

    status_filter is a list like ['pending'] or ['approved'] or ['pending', 'approved'].
    """
    if not status_filter:
        # If no filter is provided, default to pending only
        status_filter = ["pending"]

    placeholders = ", ".join([f":s{i}" for i in range(len(status_filter))])
    params = {f"s{i}": status_filter[i] for i in range(len(status_filter))}

    query = text(
        f"""
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
    )

    try:
        result = db.session.execute(query, params).fetchall()
    except Exception as e:
        logger.error(
            f"Error in get_filtered_claims_db with status_filter={status_filter}: {e}"
        )
        raise

    final_result = []
    for row in result:
        d = dict(row._mapping)
        if d.get("answers"):
            try:
                d["answers"] = (
                    json.loads(d["answers"])
                    if isinstance(d["answers"], str)
                    else d["answers"]
                )
            except Exception as parse_err:
                logger.warning(
                    f"Failed to parse answers JSON for claim {d.get('id')}: {parse_err}"
                )
        final_result.append(d)
    return final_result


def get_all_completed_claims_db():
    query = text(
        """
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
    )
    result = db.session.execute(query).fetchall()

    final_result = []
    for row in result:
        d = dict(row._mapping)
        if d.get("answers"):
            try:
                d["answers"] = (
                    json.loads(d["answers"])
                    if isinstance(d["answers"], str)
                    else d["answers"]
                )
            except:
                pass
        final_result.append(d)
    return final_result


def update_claim_status(claim_id, new_status):
    try:
        validate_int(claim_id, "claim_id")
        query = text("UPDATE claims SET decision = :status WHERE id = :id")
        res = db.session.execute(query, {"status": new_status, "id": claim_id})
        db.session.commit()
        if res.rowcount == 0:
            return {"error": "Claim not found"}, 404
        log_action("update_status", "claim", claim_id, "system")
        return {"message": "Claim status updated"}, 200
    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")
        return {"error": "Failed to update status"}, 500


def update_claim(claim_id, data):
    try:
        validate_int(claim_id, "claim_id")
        ALLOWED_FIELDS = {"claimant_name", "claimant_email", "answers", "decision"}

        updates = []
        params = {"id": claim_id}
        for key, value in data.items():
            if key in ALLOWED_FIELDS:
                updates.append(f"{key} = :{key}")
                params[key] = (
                    json.dumps(value)
                    if key == "answers" and not isinstance(value, str)
                    else value
                )

        if not updates:
            return {"error": "No valid fields to update"}, 400

        query = text(
            f"UPDATE claims SET {', '.join(updates)} WHERE id = :id"
        )  # nosec B608
        db.session.execute(query, params)
        db.session.commit()

        log_action("update", "claim", claim_id, "system")
        return {"message": "Claim updated successfully"}, 200
    except Exception as e:
        logger.error(f"Error updating claim: {str(e)}")
        return {"error": "Failed to update claim"}, 500


def verify_claim(claim_id, decision, admin_username, handover_notes=None):
    try:
        validate_int(claim_id, "claim_id")
        validate_claim_decision(decision)

        select_query = text(
            "SELECT found_item_id, lost_item_id, decision FROM claims WHERE id = :id"
        )
        row = db.session.execute(select_query, {"id": claim_id}).fetchone()

        if not row:
            return {"error": "Claim not found"}, 404

        current_decision = row.decision
        found_item_id = row.found_item_id
        lost_item_id = row.lost_item_id

        if decision == "approved":
            item_id = found_item_id or lost_item_id
            if item_id:
                col = "found_item_id" if found_item_id else "lost_item_id"
                check_query = text(
                    f"SELECT id FROM claims WHERE {col} = :item_id AND decision IN ('approved', 'completed') AND id != :id"
                )  # nosec B608
                other = db.session.execute(
                    check_query, {"item_id": item_id, "id": claim_id}
                ).fetchone()
                if other:
                    return {
                        "error": "Another claim is already approved or completed for this item"
                    }, 400

        if decision == "completed":
            if current_decision != "approved":
                return {"error": "Only approved claims can be completed"}, 400

            update_query = text(
                """
                UPDATE claims 
                SET decision = :decision, handover_notes = :notes, completed_at = :now 
                WHERE id = :id
            """
            )
            db.session.execute(
                update_query,
                {
                    "decision": decision,
                    "notes": handover_notes,
                    "now": datetime.now(timezone.utc),
                    "id": claim_id,
                },
            )

            # Update item status
            if found_item_id:
                db.session.execute(
                    text("UPDATE found_items SET status = 'found' WHERE id = :id"),
                    {"id": found_item_id},
                )
            elif lost_item_id:
                db.session.execute(
                    text("UPDATE lost_items SET status = 'found' WHERE id = :id"),
                    {"id": lost_item_id},
                )
        else:
            if current_decision not in ("pending", "approved"):
                return {
                    "error": f"Claim already processed (Current status: {current_decision})"
                }, 400
            db.session.execute(
                text("UPDATE claims SET decision = :decision WHERE id = :id"),
                {"decision": decision, "id": claim_id},
            )

        db.session.commit()
        log_action(decision, "claim", claim_id, admin_username, notes=handover_notes)
        return {"message": f"Claim {decision} successfully"}, 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error verifying claim: {str(e)}")
        return {"error": "Database error while verifying claim"}, 500


def schedule_pickup(claim_id, pickup_datetime, pickup_location):
    try:
        validate_int(claim_id, "claim_id")
        query = text("SELECT decision FROM claims WHERE id = :id")
        row = db.session.execute(query, {"id": claim_id}).fetchone()
        if not row or row.decision != "approved":
            return {"error": "Scheduling only allowed for approved claims"}, 400

        db.session.execute(
            text(
                """
            UPDATE claims SET pickup_datetime = :dt, pickup_location = :loc WHERE id = :id
        """
            ),
            {"dt": pickup_datetime, "loc": pickup_location, "id": claim_id},
        )
        db.session.commit()
        log_action("schedule", "claim", claim_id, "system")
        return {"message": "Pickup scheduled successfully"}, 200
    except Exception as e:
        logger.error(f"Error scheduling pickup: {str(e)}")
        return {"error": "Failed to schedule pickup"}, 500


def get_claim_detail_db(claim_id):
    query = text(
        """
        SELECT
            c.id AS claim_id,
            c.*, 
            u.username AS user_name,
            COALESCE(f.id, l.id) AS item_id,
            COALESCE(f.category, l.category) AS category,
            COALESCE(f.item_type, l.item_type) AS item_type,
            COALESCE(f.found_location, l.last_seen_location) AS location,
            COALESCE(f.main_picture, l.main_picture) AS main_picture,
            COALESCE(f.color, l.color) AS item_color,
            COALESCE(f.brand, l.brand) AS item_brand,
            l.last_seen_datetime AS lost_date,
            f.found_datetime AS found_date,
            COALESCE(f.public_description, l.public_description) AS item_description,
            COALESCE(f.created_at, l.created_at) AS item_reported_at
        FROM claims c
        LEFT JOIN users u ON c.user_id = u.id
        LEFT JOIN found_items f ON c.found_item_id = f.id
        LEFT JOIN lost_items l ON c.lost_item_id = l.id
        WHERE c.id = :id
    """
    )
    row = db.session.execute(query, {"id": claim_id}).fetchone()
    if not row:
        return None
    d = dict(row._mapping)
    if d.get("answers"):
        try:
            d["answers"] = (
                json.loads(d["answers"])
                if isinstance(d["answers"], str)
                else d["answers"]
            )
        except Exception:
            pass
    return d


def get_claims_db(user_id):
    query = text(
        """
        SELECT c.*, c.id AS claim_id, c.decision AS status,
               u.username AS user_name,
               COALESCE(f.item_type, l.item_type) AS item_type,
               COALESCE(f.category, l.category) AS category,
               COALESCE(f.found_datetime, l.last_seen_datetime) AS incident_date
        FROM claims c
        LEFT JOIN users u ON c.user_id = u.id
        LEFT JOIN found_items f ON c.found_item_id = f.id
        LEFT JOIN lost_items l ON c.lost_item_id = l.id
        WHERE c.user_id = :id AND (c.is_dismissed = FALSE OR c.is_dismissed IS NULL)
        ORDER BY c.created_at DESC
    """
    )
    result = db.session.execute(query, {"id": user_id}).fetchall()
    final = []
    for row in result:
        d = dict(row._mapping)
        if d.get("answers"):
            try:
                d["answers"] = (
                    json.loads(d["answers"])
                    if isinstance(d["answers"], str)
                    else d["answers"]
                )
            except Exception:
                pass
        final.append(d)
    return final


def dismiss_claim_db(claim_id, user_id):
    try:
        db.session.execute(
            text(
                "UPDATE claims SET is_dismissed = TRUE WHERE id = :id AND user_id = :uid"
            ),
            {"id": claim_id, "uid": user_id},
        )
        db.session.commit()
        return {"message": "Claim dismissed successfully"}, 200
    except Exception as e:
        logger.error(f"Error dismissing claim: {str(e)}")
        return {"error": "Failed to dismiss"}, 500
