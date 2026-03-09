# Hirely — AI-Powered Resume Screening App

Hirely is a Streamlit recruiting dashboard that helps recruiters screen resumes against a job description using NLP and semantic similarity.

## Features

- Upload and parse multiple PDF resumes
- NLP-based preprocessing and skill extraction
- Job description + required skills input flow
- Semantic matching using Sentence Transformers (`all-MiniLM-L6-v2`)
- Candidate ranking with weighted score blending semantic and skill-match signals
- Candidate insights including skill gaps and comparison charts

## Project Structure

- `app.py` — Streamlit UI and page navigation
- `ml_pipeline.py` — preprocessing, embeddings, ranking logic
- `resume_parser.py` — PDF text extraction (PyMuPDF)
- `skill_extractor.py` — dictionary-based skill extraction
- `utils.py` — shared constants, helpers, candidate schema
- `.streamlit/config.toml` — Streamlit app configuration
- `runtime.txt` — Python runtime pin for Streamlit Cloud

## Python / Dependency Compatibility (Streamlit Cloud)

This project pins a spaCy-compatible runtime to avoid `pydantic.v1` import issues seen on unsupported Python versions:

- Python: `3.11` (`runtime.txt`)
- spaCy: `3.7.2`
- pydantic: `1.10.13`

## Machine Learning Pipeline

1. **Resume Parsing**: Extract text from uploaded PDF files via PyMuPDF.
2. **Text Preprocessing**: Lowercase, stopword/punctuation removal, and token normalization via spaCy.
3. **Skill Extraction**: Match skills against a predefined dictionary.
4. **Text Embeddings**: Encode job/resume text using `all-MiniLM-L6-v2`.
5. **Similarity Scoring**: Compute cosine similarity and map to a 0–100 scale.
6. **Skill Gap Analysis**: Compare required skills with extracted skills and identify missing skills.

## Run Locally

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

> `ml_pipeline.py` also attempts to download `en_core_web_sm` automatically if the model is missing.

## Usage

1. Open **Create Job Description** and save role details.
2. Open **Upload Resumes** and upload multiple `.pdf` resumes.
3. Click **Process Resumes**.
4. Open **Candidate Ranking** and click **Run Ranking**.
5. Explore **Candidate Insights** charts and profile-level explanations.
