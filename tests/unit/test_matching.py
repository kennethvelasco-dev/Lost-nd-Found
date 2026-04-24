import pytest
from datetime import datetime, timedelta
from backend.app.utils.formatter import format_item_description
from backend.app.services.scoring_service import compute_claim_score


def test_sentence_splicing_found():
    item = {
        "category": "Wallet",
        "item_type": "Leather Wallet",
        "color": "Black",
        "brand": "Bellroy",
        "found_location": "Science Library",
    }
    assert (
        format_item_description(item)
        == "A Black Bellroy Leather Wallet found at Science Library"
    )


def test_sentence_splicing_lost_partial():
    item = {"category": "Phone", "item_type": "Unknown", "last_seen_location": "Gym"}
    assert format_item_description(item) == "A Phone lost at Gym"


def test_sentence_splicing_vowel_prefix():
    item = {"category": "Earphones", "item_type": "Electronic", "brand": "Apple"}
    assert format_item_description(item) == "An Apple Electronic"


def test_scoring_logic_exact_match():
    target_date = datetime.now()
    found_item = {
        "category": "Electronics",
        "item_type": "Laptop",
        "color": "Silver",
        "brand": "Apple",
        "found_datetime": target_date.isoformat(),
    }

    claim = {
        "claimed_category": "Electronics",
        "claimed_item_type": "Laptop",
        "claimed_color": "Silver",
        "claimed_brand": "Apple",
        "lost_datetime_claimed": target_date.isoformat(),
    }

    result = compute_claim_score(claim, found_item)
    assert result["total"] >= 100


def test_scoring_logic_date_tolerance():
    target_date = datetime.now()
    found_item = {"found_datetime": target_date.isoformat()}

    # Within 3 days
    close_date = target_date + timedelta(days=2)
    claim_close = {"lost_datetime_claimed": close_date.isoformat()}
    result_close = compute_claim_score(claim_close, found_item)
    # The 'date' rule weight is 20. If matched, it should contribute 20.
    date_breakdown = next(b for b in result_close["breakdown"] if b["field"] == "date")
    assert date_breakdown["matched"] is True

    # Beyond tolerance (10 days)
    far_date = target_date + timedelta(days=10)
    claim_far = {"lost_datetime_claimed": far_date.isoformat()}
    result_far = compute_claim_score(claim_far, found_item)
    date_breakdown_far = next(
        b for b in result_far["breakdown"] if b["field"] == "date"
    )
    assert date_breakdown_far["matched"] is False
