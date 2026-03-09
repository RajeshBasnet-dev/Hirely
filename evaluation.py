from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ml_pipeline import preprocess_text, rank_candidates


@dataclass
class EvalCase:
    job_description: str
    required_skills: list[str]
    candidates: list[dict]
    relevant_candidates: set[str]


def precision_at_k(ranked_names: list[str], relevant: set[str], k: int) -> float:
    top_k = ranked_names[:k]
    if k == 0:
        return 0.0
    return sum(1 for name in top_k if name in relevant) / k


def recall_at_k(ranked_names: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top_k = ranked_names[:k]
    hits = sum(1 for name in top_k if name in relevant)
    return hits / len(relevant)


def reciprocal_rank(ranked_names: list[str], relevant: set[str]) -> float:
    for idx, name in enumerate(ranked_names, 1):
        if name in relevant:
            return 1.0 / idx
    return 0.0


def evaluate_case(case: EvalCase, k: int = 3) -> dict[str, float]:
    ranked = rank_candidates(
        job_text=preprocess_text(case.job_description),
        candidates=case.candidates,
        required_skills=case.required_skills,
    )
    ranked_names = [item["name"] for item in ranked]

    return {
        "precision@k": round(precision_at_k(ranked_names, case.relevant_candidates, k), 3),
        "recall@k": round(recall_at_k(ranked_names, case.relevant_candidates, k), 3),
        "mrr": round(reciprocal_rank(ranked_names, case.relevant_candidates), 3),
    }


def evaluate_benchmark(cases: Iterable[EvalCase], k: int = 3) -> dict[str, float]:
    scores = [evaluate_case(case, k=k) for case in cases]
    if not scores:
        return {"precision@k": 0.0, "recall@k": 0.0, "mrr": 0.0}

    return {
        "precision@k": round(sum(s["precision@k"] for s in scores) / len(scores), 3),
        "recall@k": round(sum(s["recall@k"] for s in scores) / len(scores), 3),
        "mrr": round(sum(s["mrr"] for s in scores) / len(scores), 3),
    }


if __name__ == "__main__":
    benchmark = [
        EvalCase(
            job_description="Looking for an NLP engineer with Python, SQL, Transformers, and MLOps experience.",
            required_skills=["Python", "SQL", "NLP", "Hugging Face Transformers", "MLOps"],
            relevant_candidates={"Alice Johnson", "Ben Torres"},
            candidates=[
                {
                    "name": "Alice Johnson",
                    "resume_text": "",
                    "cleaned_text": preprocess_text("Python NLP engineer using Hugging Face Transformers and MLflow with SQL."),
                    "extracted_skills": ["Python", "NLP", "Hugging Face Transformers", "MLflow", "SQL", "MLOps"],
                },
                {
                    "name": "Ben Torres",
                    "resume_text": "",
                    "cleaned_text": preprocess_text("Machine learning engineer with Python, SQL, Docker, and MLOps pipelines."),
                    "extracted_skills": ["Python", "SQL", "Docker", "MLOps"],
                },
                {
                    "name": "Carla Smith",
                    "resume_text": "",
                    "cleaned_text": preprocess_text("Frontend engineer with React and TypeScript."),
                    "extracted_skills": ["React", "TypeScript"],
                },
            ],
        ),
        EvalCase(
            job_description="Need data analyst with SQL, Tableau, dashboarding, and business analysis.",
            required_skills=["SQL", "Tableau", "Data Analysis", "Business Analysis"],
            relevant_candidates={"Dina Park"},
            candidates=[
                {
                    "name": "Dina Park",
                    "resume_text": "",
                    "cleaned_text": preprocess_text("Data analyst with SQL Tableau and business analysis stakeholder reporting."),
                    "extracted_skills": ["SQL", "Tableau", "Data Analysis", "Business Analysis"],
                },
                {
                    "name": "Eric Hall",
                    "resume_text": "",
                    "cleaned_text": preprocess_text("Backend developer with Java Spring PostgreSQL."),
                    "extracted_skills": ["Java", "Spring Boot", "PostgreSQL"],
                },
            ],
        ),
    ]

    print("Benchmark:", evaluate_benchmark(benchmark, k=2))
