# Hirely — Resume Screener

Hirely is a portfolio-grade resume screening platform built with Streamlit and a hybrid NLP ranking engine. It parses resumes, extracts skills from a large skill taxonomy, computes semantic relevance to a job description, and ranks candidates with transparent scoring and persisted results in SQLite.

## Project Overview

Hirely helps recruiters and hiring teams:
- Upload and parse PDF resumes.
- Store jobs, candidates, and ranking outputs in a local database.
- Rank candidates using **hybrid scoring** (semantic relevance + required skill coverage).
- Inspect candidate-level explanations for decision support.
- Evaluate ranking quality with benchmark metrics.

## Features

- **Multi-page Streamlit dashboard** for end-to-end screening workflow.
- **Dynamic skill extraction** using a JSON taxonomy (`data/skills.json`) with 600+ skills.
- **Hybrid ranking engine**:
  - Semantic similarity (TF-IDF + cosine similarity)
  - Skill match ratio against required skills
- **Persistent storage** via SQLite (`hirely.db`) with tables for jobs, candidates, results.
- **Evaluation module** with Precision@K, Recall@K, and MRR.
- **Explainable outputs** showing semantic score, skill match %, and missing skills.

## System Architecture

```text
User Upload Resume
        ↓
PDF Parser (PyMuPDF)
        ↓
Text Preprocessing
        ↓
Skill Extraction (skills.json taxonomy)
        ↓
Semantic Similarity Engine (TF-IDF + Cosine)
        ↓
Hybrid Ranking Engine
        ↓
SQLite Storage (jobs, candidates, results)
        ↓
Streamlit Dashboard
```

## NLP Pipeline

1. **PDF parsing** (`resume_parser.py`) extracts text from uploaded resumes.
2. **Preprocessing** (`ml_pipeline.py`) normalizes and tokenizes text.
3. **Skill extraction** (`skill_extractor.py`) matches normalized terms from `data/skills.json`.
4. **Semantic scoring** computes cosine similarity between the job text and each candidate profile.
5. **Hybrid ranking** blends semantic similarity and skill coverage.

## Scoring Algorithm

For each candidate:

- `semantic_similarity` ∈ [0, 1]
- `skill_match_ratio` ∈ [0, 1]

Final score:

```text
final_score = (0.7 * semantic_similarity + 0.3 * skill_match_ratio) * 100
```

This avoids misleading scaling and ensures normalization to 0–100 only at the end.

## Data Model & Persistence

### SQLite tables

- `jobs`: title, description, required skills
- `candidates`: parsed resume text, cleaned text, extracted skills
- `results`: final scores + explainability fields

Database helper module: `database.py`.

## Evaluation & Benchmark

`evaluation.py` includes:
- A mini benchmark dataset with expected relevant candidates.
- Ranking metrics:
  - Precision@K
  - Recall@K
  - Mean Reciprocal Rank (MRR)

Run:

```bash
python evaluation.py
```

## Example Ranking Output

| Rank | Candidate | Semantic % | Skill Match % | Final Match % | Missing Skills |
|------|-----------|------------|---------------|---------------|----------------|
| 1 | Alice Johnson | 84.3 | 100.0 | 88.99 | None |
| 2 | Ben Torres | 73.6 | 80.0 | 75.52 | Hugging Face Transformers |
| 3 | Carla Smith | 21.0 | 0.0 | 14.70 | Python, SQL, NLP, MLOps |

## Screenshots

> Add screenshots by running the app locally and capturing Dashboard, Ranking, and Insights pages.

## Setup Instructions

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```text
hirely/
├── app.py
├── ml_pipeline.py
├── resume_parser.py
├── database.py
├── evaluation.py
├── skill_extractor.py
├── utils.py
├── data/
│   └── skills.json
├── requirements.txt
└── README.md
```

## Why this is portfolio-ready

- Clean separation of UI, NLP pipeline, and persistence.
- Explainable and reproducible ranking outputs.
- Benchmark-oriented evaluation for technical review.
- Lightweight and deployable architecture without heavyweight infra.
