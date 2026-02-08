from backend.services.scoring_service import compute_claim_score

def make_found_item():
    return {
        "category": "Electronics",
        "item_type": "Phone",
        "brand": "Samsung",
        "color": "Black",
        "public_description": "Cracked screen"
    }

def test_exact_match_scores_full_points():
    claim = {
        "claimed_category": "Electronics",
        "claimed_item_type": "Phone",
        "claimed_brand": "Samsung",
        "claimed_color": "Black",
        "claimed_private_details": "Cracked screen"
    }

    score = compute_claim_score(claim, make_found_item())

    assert score["total"] == 100
    assert score["breakdown"]["brand"] == 20

def test_partial_match_gets_half_points():
    claim = {
        "claimed_brand": "Samsung Galaxy",
        "claimed_color": "Black",
    }

    score = compute_claim_score(claim, make_found_item())

    assert score["breakdown"]["brand"] == 10   # 50% of 20

def test_no_match_gets_zero():
    claim = {
        "claimed_brand": "Apple",
    }

    score = compute_claim_score(claim, make_found_item())

    assert score["breakdown"]["brand"] == 0

def test_breakdown_is_explainable():
    claim = {
        "claimed_category": "Electronics",
        "claimed_item_type": "Phone",
    }

    score = compute_claim_score(claim, make_found_item())

    assert "total" in score
    assert "breakdown" in score
    assert isinstance(score["breakdown"], dict)

def test_total_is_integer():
    claim = {}
    score = compute_claim_score(claim, make_found_item())
    assert isinstance(score["total"], int)
