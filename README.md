# Hirely — AI-Powered Resume Screening App

Hirely is a Streamlit recruiting dashboard that helps recruiters screen resumes against a job description using NLP preprocessing, skill extraction, and semantic ranking.

## Why spaCy breaks on Python 3.14

Your error:

`pydantic.v1.errors.ConfigError: unable to infer type for attribute "REGEX"`

is a compatibility issue in the legacy dependency chain:

- spaCy 3.x internally depends on pydantic v1 models in multiple schema modules.
- pydantic v1 is legacy and not maintained for new Python runtime internals at the same level as pydantic v2.
- On Python 3.14, importing spaCy can trigger pydantic v1 model construction failures (including `REGEX` inference errors), causing startup failures before app code runs.

## Python 3.14-compatible solution in this repo

This project was refactored to remove runtime dependency on spaCy/pydantic v1:

- Text preprocessing now uses regex + stopword filtering.
- Semantic similarity now uses `TfidfVectorizer` + cosine similarity from scikit-learn.
- Skill extraction remains dictionary-based regex matching.
- Candidate ranking blends semantic similarity with required-skill coverage.

## Requirements

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```text
Hirely/
├── app.py
├── ml_pipeline.py
├── requirements.txt
```

## Notes on alternatives

If you want deeper NLP later without spaCy, this codebase is ready for drop-in enrichment with:

- `stanza` for linguistic pipelines
- `transformers` for contextual embeddings/classification
- `nltk` for additional lexical processing
- scikit-learn text processing for lightweight deployment
