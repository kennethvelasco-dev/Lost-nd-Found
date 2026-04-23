from datetime import datetime, timedelta
from ..config.claim_scoring import SCORING_RULES


def normalize(value):
    return value.strip().lower() if value else ""


def matches(a, b):
    return normalize(a) == normalize(b)


def match_with_tolerance(claim_value, found_value, tolerance):
    if not claim_value or not found_value:
        return False

    # Date proximity check
    if isinstance(tolerance, str) and tolerance.startswith("days_"):
        try:
            days_limit = int(tolerance.split("_")[1])
            d1 = datetime.fromisoformat(str(claim_value).replace("Z", "+00:00"))
            d2 = datetime.fromisoformat(str(found_value).replace("Z", "+00:00"))
            return abs((d1 - d2).days) <= days_limit
        except (ValueError, TypeError, AttributeError):
            return False

    a = normalize(str(claim_value))
    b = normalize(str(found_value))

    matchers = {"exact": lambda x, y: x == y, "contains": lambda x, y: x in y or y in x}

    return matchers.get(tolerance, lambda x, y: x == y)(a, b)


def compute_claim_score(claim_data: dict, found_item: dict) -> dict:
    """
    Compute a claim score based on matching fields with the found item.
    Uses SCORING_RULES from config.
    """
    total_score = 0
    matched_fields = []
    breakdown = []

    # Map claim fields to found item fields
    # Unified mapping to support both 'found_items' and 'lost_items' tables
    field_map = {
        "category": ("claimed_category", "category"),
        "item_type": ("claimed_item_type", "item_type"),
        "brand": ("claimed_brand", "brand"),
        "color": ("claimed_color", "color"),
        "location": ("lost_location_claimed", ["found_location", "last_seen_location"]),
        "private_details": (
            "claimed_private_details",
            ["public_description", "private_details"],
        ),
        "date": ("lost_datetime_claimed", ["found_datetime", "last_seen_datetime"]),
    }

    for field, (claim_key, found_keys) in field_map.items():
        rule = SCORING_RULES.get(field)
        if not rule:
            continue

        claim_val = claim_data.get(claim_key)

        # Handle multiple possible found item keys (for lost/found table unification)
        found_val = None
        if isinstance(found_keys, list):
            for k in found_keys:
                if k in found_item:
                    found_val = found_item[k]
                    break
        else:
            found_val = found_item.get(found_keys)

        matched = match_with_tolerance(claim_val, found_val, rule["tolerance"])

        earned = rule["weight"] if matched else 0
        total_score += earned

        if matched:
            matched_fields.append(field)

        breakdown.append(
            {
                "field": field,
                "matched": matched,
                "score": earned,
                "max_score": rule["weight"],
            }
        )

    return {"total": total_score, "matched": matched_fields, "breakdown": breakdown}


def calculate_match_confidence(claim_data: dict, found_item: dict) -> dict:
    """
    Alias for compute_claim_score to provide semantic clarity during complete transaction flow.
    """
    return compute_claim_score(claim_data, found_item)
