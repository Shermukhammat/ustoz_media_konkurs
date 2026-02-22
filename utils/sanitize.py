import re

def sanitize_name(name: str | None) -> str:
    """
    Keep only Latin letters (a-z A-Z), Cyrillic letters (а-я А-Я ёЁ),
    digits (0-9), and spaces.  Everything else (emoji, punctuation, special
    symbols, curly braces, etc.) is removed so the value is safe to use
    inside str.format() template strings sent with an HTML/Markdown parse mode.
    """
    if not name:
        return ""
    # Allow: Latin, Cyrillic (basic + Ё/ё), digits, space
    cleaned = re.sub(r"[^a-zA-Z\u0400-\u04FF0-9 ]", "", name)
    return cleaned.strip()
