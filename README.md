Hirely — AI-Powered Resume Screening Platform

Hirely is a lightweight AI-driven resume screening application built with Streamlit. It enables recruiters to quickly evaluate candidate resumes against a job description using natural language processing techniques such as text preprocessing, skill extraction, and semantic similarity ranking.

The system analyzes uploaded resumes and ranks candidates based on how closely their profiles match the required job criteria.

Key Features

Automated Resume Screening
Evaluates resumes against job descriptions to identify the most relevant candidates.

Semantic Resume Matching
Uses TF-IDF vectorization and cosine similarity to measure alignment between resumes and job requirements.

Skill Extraction
Detects relevant technical and domain-specific skills using pattern-based extraction.

Candidate Ranking
Scores and ranks candidates based on semantic similarity and skill coverage.

Interactive Dashboard
Built with Streamlit for easy uploading, analysis, and visualization of candidate rankings.
Refactored Architecture

To ensure full compatibility with Python 3.14, this project removes the dependency on spaCy and instead uses lightweight NLP techniques built on standard Python libraries.

Current Processing Pipeline

Text Preprocessing

Regex-based text cleaning

Stopword filtering

Normalization

Feature Extraction

TfidfVectorizer from scikit-learn

Semantic Similarity

Cosine similarity between job descriptions and resumes

Skill Matching

Regex-based dictionary extraction for relevant skills

Candidate Ranking

Combined scoring based on semantic similarity and skill coverage

This approach keeps the application lightweight, fast, and deployable without large NLP dependencies.

Installation

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py
Project Structure
Hirely/
│
├── app.py            # Streamlit application interface
├── ml_pipeline.py    # Resume processing and ranking logic
├── requirements.txt  # Project dependencies
Future Enhancements

The current architecture allows easy integration of more advanced NLP systems if deeper analysis is required.

Potential upgrades include:

Transformers (Hugging Face) — contextual embeddings for improved semantic matching

Stanza — full linguistic pipelines

NLTK — expanded lexical analysis

Sentence Transformers — semantic embeddings for high-accuracy resume ranking

These can be added without major changes to the current pipeline.

Use Cases

Hirely is suitable for:

HR teams screening large volumes of resumes

Early-stage recruiting automation

AI/ML demo projects for recruitment technology

Educational NLP and machine learning projects

License

This project is intended for educational and demonstration purposes.
