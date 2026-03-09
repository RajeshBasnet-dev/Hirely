from __future__ import annotations

from typing import Dict, Iterable, List
import re

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills


TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]*")


def preprocess_text(text: str) -> str:
    """Normalize resume/job text using regex tokenization and stop-word removal.

    This implementation intentionally avoids spaCy/pydantic dependencies so it works
    cleanly on Python 3.14.
    """
    lowered = text.lower()
    tokens = TOKEN_PATTERN.findall(lowered)
    filtered = [token for token in tokens if token not in ENGLISH_STOP_WORDS]
    return " ".join(filtered)


def analyze_resume(resume_text: str, skill_dictionary: Iterable[str]) -> Dict:
    cleaned = preprocess_text(resume_text)
    skills = extract_skills(cleaned, skill_dictionary)
    return {
        "cleaned_text": cleaned,
        "skills": skills,
    }


def _build_similarity_scores(job_text: str, candidate_texts: List[str]) -> np.ndarray:
    corpus = [job_text] + candidate_texts
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    job_vector = tfidf_matrix[0:1]
    candidate_vectors = tfidf_matrix[1:]
    return cosine_similarity(job_vector, candidate_vectors).flatten()


def rank_candidates(job_text: str, candidates: List[Dict], required_skills: Iterable[str]) -> List[Dict]:
    if not candidates:
        return []

    required_lower = {skill.lower().strip() for skill in required_skills if skill.strip()}

    similarities = _build_similarity_scores(job_text, [candidate["cleaned_text"] for candidate in candidates])

    ranked: List[Dict] = []
    for idx, candidate in enumerate(candidates):
        semantic_score = float(np.clip(similarities[idx], 0.0, 1.0) * 100)

        candidate_skill_set = {skill.lower() for skill in candidate.get("extracted_skills", [])}
        missing = sorted(skill for skill in required_lower if skill not in candidate_skill_set)
        skill_match = (1 - (len(missing) / max(1, len(required_lower)))) * 100 if required_lower else 100

        blended_score = (0.7 * semantic_score) + (0.3 * skill_match)

        ranked.append(
            {
                **candidate,
                "match_score": round(blended_score, 2),
                "missing_skills": [skill.title() for skill in missing],
                "skill_match_pct": round(skill_match, 2),
                "semantic_score": round(semantic_score, 2),
            }
        )

    ranked.sort(key=lambda item: item["match_score"], reverse=True)
    return ranked
