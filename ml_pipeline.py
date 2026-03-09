from __future__ import annotations

from typing import Iterable, List, Dict
import re
import subprocess
import sys

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills


def _import_spacy():
    try:
        import spacy  # type: ignore

        return spacy
    except Exception:
        # Covers ImportError and spaCy/pydantic compatibility failures on unsupported Python versions.
        return None


def load_spacy_model():
    """Load spaCy model if available; otherwise return None and use fallback preprocessing."""
    spacy = _import_spacy()
    if spacy is None:
        return None

    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            return None


class NLPResources:
    def __init__(self) -> None:
        self._nlp = None
        self._model = None

    @property
    def nlp(self):
        if self._nlp is None:
            self._nlp = load_spacy_model()
        return self._nlp

    @property
    def sentence_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model


resources = NLPResources()


def _fallback_preprocess_text(text: str) -> str:
    lowered = text.lower()
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", lowered)
    filtered = [tok for tok in tokens if tok not in ENGLISH_STOP_WORDS]
    return " ".join(filtered)


def preprocess_text(text: str) -> str:
    nlp = resources.nlp
    if nlp is None:
        return _fallback_preprocess_text(text)

    doc = nlp(text.lower())
    tokens = [
        tok.lemma_.strip() if tok.lemma_ else tok.text.strip()
        for tok in doc
        if tok.text.strip() and not tok.is_stop and not tok.is_punct
    ]
    return " ".join(t for t in tokens if t)


def analyze_resume(resume_text: str, skill_dictionary: Iterable[str]) -> Dict:
    cleaned = preprocess_text(resume_text)
    skills = extract_skills(cleaned, skill_dictionary)
    return {"cleaned_text": cleaned, "skills": skills}


def rank_candidates(job_text: str, candidates: List[Dict], required_skills: Iterable[str]) -> List[Dict]:
    if not candidates:
        return []

    required_lower = {s.lower().strip() for s in required_skills if s.strip()}

    corpus = [job_text] + [c["cleaned_text"] for c in candidates]
    embeddings = resources.sentence_model.encode(corpus)
    job_embedding = embeddings[0].reshape(1, -1)
    resume_embeddings = embeddings[1:]

    sims = cosine_similarity(job_embedding, resume_embeddings).flatten()

    ranked = []
    for idx, candidate in enumerate(candidates):
        similarity = float(np.clip(sims[idx], -1, 1))
        score = max(0.0, min(100.0, (similarity + 1) * 50))

        candidate_skill_set = {s.lower() for s in candidate["extracted_skills"]}
        missing = sorted([s for s in required_lower if s not in candidate_skill_set])
        skill_match = (1 - (len(missing) / max(1, len(required_lower)))) * 100 if required_lower else 100

        blended_score = 0.7 * score + 0.3 * skill_match

        updated = {
            **candidate,
            "match_score": round(blended_score, 2),
            "missing_skills": [m.title() for m in missing],
            "skill_match_pct": round(skill_match, 2),
            "semantic_score": round(score, 2),
        }
        ranked.append(updated)

    ranked.sort(key=lambda c: c["match_score"], reverse=True)
    return ranked
