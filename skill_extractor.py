from __future__ import annotations

from typing import Iterable, List
import re


def extract_skills(text: str, skill_dictionary: Iterable[str]) -> List[str]:
    text_lower = text.lower()
    found: list[str] = []
    for skill in skill_dictionary:
        escaped = re.escape(skill.lower())
        if re.search(rf"\b{escaped}\b", text_lower):
            found.append(skill)
    return sorted(found)
