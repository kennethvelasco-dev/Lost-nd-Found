def format_item_description(item_data):
    """
    Constructs a human-readable sentence from item attributes.
    Example: "A Black Bellroy Leather Wallet found at Science Library"
    """
    category = item_data.get("category", "Item")
    item_type = item_data.get("item_type")
    color = item_data.get("color")
    brand = item_data.get("brand")

    # Handle both original schemas and unified search results
    found_loc = item_data.get("found_location")
    lost_loc = item_data.get("last_seen_location")
    raw_loc = item_data.get("location")  # Used in search results

    # Determine the location and type
    location = found_loc or lost_loc or raw_loc
    is_found = found_loc is not None or (
        raw_loc is not None and item_data.get("source_table") == "found"
    )

    parts = []

    if color:
        parts.append(color.capitalize())
    if brand:
        parts.append(brand)
    if item_type and item_type.lower() != "unknown":
        parts.append(item_type)
    else:
        parts.append(category)

    description = " ".join(parts)

    # Prefix with 'A' or 'An'
    if description:
        vowels = ("a", "e", "i", "o", "u")
        prefix = "An" if description[0].lower() in vowels else "A"
        description = f"{prefix} {description}"
    else:
        description = f"A {category}"

    if location:
        verb = "found" if is_found else "lost"
        description += f" {verb} at {location}"

    return description
