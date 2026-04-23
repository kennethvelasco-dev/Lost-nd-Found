def splice_sentence(attributes: dict) -> str:
    """
    Format item attributes into a readable sentence.
    Example: {'color': 'Red', 'brand': 'Nike', 'item_type': 'Shoes'}
    -> "Red Nike Shoes"
    """
    parts = []

    # Order of importance for a natural sentence
    order = ["color", "brand", "item_type"]

    for key in order:
        val = attributes.get(key)
        if val and val.lower() not in ["unknown", "none", ""]:
            parts.append(val.strip())

    if not parts:
        return attributes.get("category", "Item")

    return " ".join(parts)
