from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Iterable, List
import re

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills
from utils import RankedCandidate


TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]*")


def preprocess_text(text: str) -> str:
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
        semantic_similarity = float(np.clip(similarities[idx], 0.0, 1.0))

        candidate_skill_set = {skill.lower() for skill in candidate.get("extracted_skills", [])}
        overlap = len(required_lower.intersection(candidate_skill_set))
        skill_match_ratio = overlap / max(1, len(required_lower)) if required_lower else 1.0
        missing = sorted(skill for skill in required_lower if skill not in candidate_skill_set)

        final_score = ((0.7 * semantic_similarity) + (0.3 * skill_match_ratio)) * 100

        ranked_candidate = RankedCandidate(
            name=candidate["name"],
            resume_text=candidate["resume_text"],
            cleaned_text=candidate["cleaned_text"],
            extracted_skills=candidate.get("extracted_skills", []),
            match_score=round(final_score, 2),
            semantic_score=round(semantic_similarity * 100, 2),
            skill_match_pct=round(skill_match_ratio * 100, 2),
            missing_skills=[skill.title() for skill in missing],
        )
        candidate_dict = asdict(ranked_candidate)
        if "id" in candidate:
            candidate_dict["id"] = candidate["id"]
        ranked.append(candidate_dict)

    ranked.sort(key=lambda item: item["match_score"], reverse=True)
    return ranked
