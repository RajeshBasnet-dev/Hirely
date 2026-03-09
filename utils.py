from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, List, Dict, Any
import re


SKILL_DICTIONARY: List[str] = [
    "Python",
    "SQL",
    "Machine Learning",
    "Django",
    "React",
    "Data Analysis",
    "Statistics",
    "Deep Learning",
    "NLP",
    "TensorFlow",
    "PyTorch",
    "AWS",
    "Docker",
    "Git",
    "FastAPI",
    "Flask",
    "Power BI",
    "Tableau",
    "Spark",
    "Pandas",
    "NumPy",
]


@dataclass
class CandidateRecord:
    name: str
    resume_text: str
    cleaned_text: str
    extracted_skills: List[str]
    match_score: float = 0.0
    missing_skills: List[str] | None = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["extracted_skills"] = ", ".join(self.extracted_skills)
        data["missing_skills"] = ", ".join(self.missing_skills or [])
        data["match_score"] = round(self.match_score, 2)
        return data


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
    # De-duplicate preserving order
    seen = set()
    unique = []
    for skill in skills:
        key = skill.lower()
        if key not in seen:
            seen.add(key)
            unique.append(skill)
    return unique
