from typing import Literal

Language = Literal["python", "java", "cpp"]


def normalize_language(value: str) -> Language:
    normalized = value.strip().lower()
    aliases = {
        "py": "python",
        "python3": "python",
        "c++": "cpp",
        "cplusplus": "cpp",
        "g++": "cpp",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"python", "java", "cpp"}:
        raise ValueError("Language must be one of: python, java, cpp")
    return normalized  # type: ignore[return-value]
