# Hirely — AI-Powered Resume Screening App

Hirely is a Streamlit recruiting dashboard that helps recruiters screen resumes against a job description using NLP and semantic similarity.

## Why you were seeing `pydantic.v1.errors.ConfigError` on Python 3.14

The error (`unable to infer type for attribute "REGEX"`) is a **runtime compatibility issue** in the dependency chain:

- `spaCy 3.x` relies on `pydantic v1`
- `pydantic v1` has compatibility gaps on `Python 3.14`
- importing spaCy on Python 3.14 can fail before your app logic runs

So this is not a bug in your Hirely business logic. The fix is to run on a supported Python runtime (3.10/3.11) and pin compatible package versions.

## Compatibility Fix Applied

- Python pinned to `3.11` (`runtime.txt`, `.python-version`)
- `spacy==3.7.2`
- `pydantic==1.10.13`

## Required Setup (Windows / Local)

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

## Streamlit Deployment Notes

This repo is prepared for Streamlit deployment with:

- `runtime.txt` (Python version)
- `.streamlit/config.toml` (app config)
- `requirements.txt` (pinned dependencies)

## Project Structure

```text
hirely/
├── app.py
├── ml_pipeline.py
├── requirements.txt
└── .streamlit/
    └── config.toml
```

(Additional files in the repo support PDF parsing, utilities, and docs.)

## Features

- Upload and parse multiple PDF resumes
- NLP preprocessing + skill extraction
- Semantic matching with sentence embeddings (`all-MiniLM-L6-v2`)
- Candidate ranking with skill-gap analysis
- Candidate insights charts in Streamlit

## Troubleshooting

### `ModuleNotFoundError: No module named "spacy"`

Install dependencies in the active virtual environment:

```bash
pip install -r requirements.txt
```

Then install the language model:

```bash
python -m spacy download en_core_web_sm
```

`ml_pipeline.py` includes a fallback preprocessing path so the app can still start if spaCy/model loading fails, but best NLP quality requires spaCy + model installed.
