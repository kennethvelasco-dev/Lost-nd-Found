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

    return matchers[tolerance](a, b)

def compute_claim_score(claim_data, found_item):
    total_score = 0
    matched_fields = []
    breakdown = []

    field_map = {
        "category": ("claimed_category", "category"),
        "item_type": ("claimed_item_type", "item_type"),
        "brand": ("claimed_brand", "brand"),
        "color": ("claimed_color", "color"),
        "location": ("claimed_location", "found_location"),
        "private_details": ("claimed_private_details", "public_description"),
    }

    for field, (claim_key, found_key) in field_map.items():
        rule = SCORING_RULES[field]

        matched = match_with_tolerance(
            claim_data.get(claim_key),
            found_item.get(found_key),
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

def compute_claim_score(claim: dict, found_item: dict) -> dict:
    """
    Compute a claim score based on matching fields with the found item.
    Returns a dict:
        {
            "total": int,
            "breakdown": {field: score, ...}
        }
    """
    WEIGHTS = {
        "category": 20,
        "item_type": 20,
        "brand": 20,
        "color": 20,
        "private_details": 20
    }

    # Mapping from claim field -> DB field in found_item
    FOUND_ITEM_FIELD_MAP = {
        "category": "found_category",
        "item_type": "found_item_type",
        "brand": "found_brand",
        "color": "color",
        "private_details": "public_description"  # or whatever you want to compare
    }

    breakdown = {}
    total = 0

    for field, weight in WEIGHTS.items():
        claim_value = claim.get(f"claimed_{field}") or ""
        found_value = found_item.get(FOUND_ITEM_FIELD_MAP.get(field, field)) or ""

        # Normalize to lowercase for comparison
        claim_value_lower = str(claim_value).lower()
        found_value_lower = str(found_value).lower()

        if claim_value_lower == found_value_lower:
            score = weight  # exact match
        elif claim_value_lower in found_value_lower or found_value_lower in claim_value_lower:
            score = weight // 2  # partial match
        else:
            score = 0

        breakdown[field] = score
        total += score

    return {"total": total, "breakdown": breakdown}