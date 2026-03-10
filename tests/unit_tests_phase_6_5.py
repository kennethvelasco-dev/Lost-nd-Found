import unittest
from backend.helpers.formatter import format_item_description
from backend.services.scoring_service import compute_claim_score
from datetime import datetime, timedelta

class TestPhase65(unittest.TestCase):
    
    def test_sentence_splicing(self):
        # Case 1: All attributes present (Found)
        item1 = {
            "category": "Wallet",
            "item_type": "Leather Wallet",
            "color": "Black",
            "brand": "Bellroy",
            "found_location": "Science Library"
        }
        self.assertEqual(
            format_item_description(item1),
            "A Black Bellroy Leather Wallet found at Science Library"
        )
        
        # Case 2: Missing attributes (Lost)
        item2 = {
            "category": "Phone",
            "item_type": "Unknown",
            "last_seen_location": "Gym"
        }
        self.assertEqual(
            format_item_description(item2),
            "A Phone lost at Gym"
        )
        
        # Case 3: Vowel prefix
        item3 = {
            "category": "Earphones",
            "item_type": "Electronic",
            "brand": "Apple"
        }
        self.assertEqual(
            format_item_description(item3),
            "An Apple Electronic"
        )

    def test_scoring_logic(self):
        # Setup data
        target_date = datetime.now()
        found_item = {
            "category": "Electronics",
            "item_type": "Laptop",
            "color": "Silver",
            "brand": "Apple",
            "found_datetime": target_date.isoformat()
        }
        
        # Exact match (using correct claimed_ prefixes)
        claim1 = {
            "claimed_category": "Electronics",
            "claimed_item_type": "Laptop",
            "claimed_color": "Silver",
            "claimed_brand": "Apple",
            "claimed_datetime": target_date.isoformat()
        }
        result1 = compute_claim_score(claim1, found_item)
        score1 = result1["total"]
        # Max score for these fields is 30+25+15+20+20 = 110 (missing location and private_details)
        self.assertGreaterEqual(score1, 100)
        
        # Close date match (3 days)
        close_date = target_date + timedelta(days=2)
        claim2 = claim1.copy()
        claim2["claimed_datetime"] = close_date.isoformat()
        result2 = compute_claim_score(claim2, found_item)
        self.assertEqual(result2["total"], score1) # Should still be same as it's within 3 days
        
        # Far date match (10 days) - should lose points from the 'date' rule (worth 20)
        far_date = target_date + timedelta(days=10)
        claim3 = claim1.copy()
        claim3["claimed_datetime"] = far_date.isoformat()
        result3 = compute_claim_score(claim3, found_item)
        self.assertEqual(result3["total"], score1 - 20)

if __name__ == "__main__":
    unittest.main()
