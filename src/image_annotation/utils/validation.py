"""Validation utilities for annotation quality control."""

from collections import Counter


def detect_repetitive_pattern(text: str, min_repeats: int = 10) -> dict | None:
    """Detect repetitive patterns in text.

    Args:
        text: Text to analyze
        min_repeats: Minimum number of repetitions to flag

    Returns:
        Dict with pattern info if found, None otherwise
    """
    # Check for simple repeating patterns (2-50 chars)
    for pattern_len in range(2, 51):
        if len(text) < pattern_len:
            continue
        pattern = text[:pattern_len]
        count = text.count(pattern)
        if count >= min_repeats:
            return {
                "pattern": pattern[:50],  # Truncate for display
                "count": count,
                "pattern_length": pattern_len,
            }

    # Check for word-level repetition
    words = text.split()
    if len(words) > 20:
        word_counts = Counter(words)
        most_common = word_counts.most_common(1)[0]
        if most_common[1] >= min_repeats:
            return {
                "pattern": f"word: {most_common[0]}",
                "count": most_common[1],
                "pattern_length": len(most_common[0]),
            }

    return None


def has_repetitive_pattern(text: str, min_repeats: int = 50) -> bool:
    """Check if text has repetitive pattern (simpler version for flagging).

    Args:
        text: Text to check
        min_repeats: Minimum repetitions to consider problematic

    Returns:
        True if repetitive pattern detected
    """
    if len(text) <= 1000:
        return False

    # Check for known corruption patterns
    sample = text[-500:]  # Check last 500 chars
    if "!#system" in sample:
        return True

    # Check for same short sequence (2-10 chars) repeated 50+ times
    for pattern_len in range(2, 11):
        if len(text) < pattern_len:
            continue
        pattern = text[:pattern_len]
        count = text.count(pattern)
        if count >= min_repeats:
            return True

    return False


def validate_structured_inventory_schema(data: dict) -> list[str]:
    """Validate structured_inventory JSON against expected schema.

    Expected structure:
    - Level 1: Only these 4 keys: 'human', 'animal', 'man-made', 'natural'
    - Level 2: Item names (any string)
    - Level 3: Only these keys: 'count', 'location', 'color', 'size', 'description'

    Args:
        data: Parsed JSON data from structured_inventory response

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    if not isinstance(data, dict):
        errors.append("Root is not a dictionary")
        return errors

    # Valid level 1 categories
    valid_categories = {"human", "animal", "man-made", "natural"}

    # Valid level 3 attribute keys
    valid_attributes = {"count", "location", "color", "size", "description"}

    # Check level 1: should only have valid categories
    invalid_categories = set(data.keys()) - valid_categories
    if invalid_categories:
        errors.append(f"Invalid level-1 categories: {invalid_categories}")

    # Check level 2 and 3
    for category, items in data.items():
        if not isinstance(items, dict):
            errors.append(f"Category '{category}' should contain a dict of items")
            continue

        for item_name, attributes in items.items():
            if not isinstance(attributes, dict):
                errors.append(f"Item '{category}.{item_name}' should have dict attributes")
                continue

            # Check for invalid attribute keys
            invalid_attrs = set(attributes.keys()) - valid_attributes
            if invalid_attrs:
                errors.append(
                    f"Item '{category}.{item_name}' has invalid attributes: {invalid_attrs}"
                )

            # Validate attribute types
            if "count" in attributes and not isinstance(attributes["count"], int):
                errors.append(f"Item '{category}.{item_name}.count' should be integer")

            if "color" in attributes and not isinstance(attributes["color"], list):
                errors.append(f"Item '{category}.{item_name}.color' should be array")

    return errors
