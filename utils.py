from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List
import json
import re


SKILLS_PATH = Path(__file__).parent / "data" / "skills.json"


def load_skill_dictionary(path: Path = SKILLS_PATH) -> List[str]:
    """Load normalized skill list from JSON file."""
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        raise ValueError("skills.json must contain a JSON list of skills")

    # normalize + de-dupe preserving order
    seen: set[str] = set()
    skills: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        skill = item.strip()
        if not skill:
            continue
        key = skill.casefold()
        if key in seen:
            continue
        seen.add(key)
        skills.append(skill)

    return skills


SKILL_DICTIONARY: List[str] = load_skill_dictionary()


@dataclass
class CandidateRecord:
    name: str
    resume_text: str
    cleaned_text: str
    extracted_skills: List[str]


@dataclass
class RankedCandidate(CandidateRecord):
    match_score: float
    semantic_score: float
    skill_match_pct: float
    missing_skills: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


def safe_candidate_name(filename: str, resume_text: str) -> str:
    """Infer candidate name from the first non-empty line, fallback to file name."""
    for line in resume_text.splitlines():
        line = line.strip()
        if len(line.split()) in (2, 3) and line and not re.search(r"[@0-9]", line):
            return line.title()
    return re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE).replace("_", " ").title()


def parse_required_skills(raw_skills: str | Iterable[str]) -> List[str]:
    if isinstance(raw_skills, str):
        parts = re.split(r"[,\n;]+", raw_skills)
    else:
        parts = list(raw_skills)

    skills = [p.strip() for p in parts if p and p.strip()]

    seen = set()
    unique = []
    for skill in skills:
        key = skill.lower()
        if key not in seen:
            seen.add(key)
            unique.append(skill)
    return unique
