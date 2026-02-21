from backend.config.claim_scoring import SCORING_RULES

def normalize(value):
    return value.strip().lower() if value else ""

def matches(a, b):
    return normalize(a) == normalize(b)

def match_with_tolerance(claim_value, found_value, tolerance):
    a = normalize(claim_value)
    b = normalize(found_value)

    if not a or not b:
        return False

    matchers = {
        "exact": lambda x, y: x == y,
        "contains": lambda x, y: x in y or y in x
    }

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
    field_map = {
        "category": ("claimed_category", "category"),
        "item_type": ("claimed_item_type", "item_type"),
        "brand": ("claimed_brand", "brand"),
        "color": ("claimed_color", "color"),
        "location": ("claimed_location", "found_location"),
        "private_details": ("claimed_private_details", "public_description"),
    }

    for field, (claim_key, found_key) in field_map.items():
        rule = SCORING_RULES.get(field)
        if not rule:
            continue

        matched = match_with_tolerance(
            str(claim_data.get(claim_key, "")),
            str(found_item.get(found_key, "")),
            rule["tolerance"]
        )

        earned = rule["weight"] if matched else 0
        total_score += earned

        if matched:
            matched_fields.append(field)

        breakdown.append({
            "field": field,
            "matched": matched,
            "score": earned,
            "max_score": rule["weight"]
        })

    return {
        "total": total_score,
        "matched": matched_fields,
        "breakdown": breakdown
    }

def calculate_match_confidence(claim_data: dict, found_item: dict) -> dict:
    """
    Alias for compute_claim_score to provide semantic clarity during complete transaction flow.
    """
    return compute_claim_score(claim_data, found_item)
