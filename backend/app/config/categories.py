CATEGORY_GROUPS = {
    "Electronics": ["Electronics", "Phones", "Laptops", "Tablets", "Cameras", "Gadgets", "Accessories"],
    "Personal Items": ["Personal Items", "Wallets", "Purse", "Keys", "Glasses", "Umbrellas"],
    "Documents": ["Documents", "ID Cards", "Passports", "Books", "Notebooks", "Papers"],
    "Clothing": ["Clothing", "Bags", "Backpacks", "Shoes", "Hats", "Accessories"],
    "Jewelry": ["Jewelry", "Watches", "Rings", "Necklaces", "Bracelets"],
    "Other": ["Other", "Miscellaneous"]
}

def get_related_categories(category):
    """Returns a list of categories related to the given one for relaxed filtering."""
    for group, members in CATEGORY_GROUPS.items():
        if category in members:
            return members
    return [category] # Fallback to just the category itself
