from __future__ import annotations

import io
from collections import Counter
import pandas as pd
import streamlit as st

from ml_pipeline import analyze_resume, preprocess_text, rank_candidates
from resume_parser import parse_pdf
from utils import CandidateRecord, SKILL_DICTIONARY, parse_required_skills, safe_candidate_name


st.set_page_config(page_title="Hirely — AI Resume Screening", page_icon="🧠", layout="wide")


CUSTOM_CSS = """
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.hirely-card {background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 1rem 1.2rem;}
.hirely-muted {color: #94a3b8; font-size: 0.9rem;}
.hirely-header {font-size: 1.5rem; font-weight: 700; margin-bottom: 0.4rem;}
.score-label {font-size: 0.85rem; color: #94a3b8; margin-top: 0.2rem;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "job" not in st.session_state:
    st.session_state.job = {"title": "", "description": "", "required_skills": []}
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "ranked_candidates" not in st.session_state:
    st.session_state.ranked_candidates = []


with st.sidebar:
    st.title("Hirely")
    page = st.radio(
        "Navigation",
        ["Dashboard", "Create Job Description", "Upload Resumes", "Candidate Ranking", "Candidate Insights"],
    )


st.markdown(f"<div class='hirely-header'>{page}</div>", unsafe_allow_html=True)

if page == "Dashboard":
    candidates = st.session_state.candidates
    ranked = st.session_state.ranked_candidates
    total = len(candidates)
    avg_score = round(sum(c.get("match_score", 0) for c in ranked) / len(ranked), 2) if ranked else 0.0
    top_name = ranked[0]["name"] if ranked else "—"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Resumes Uploaded", total)
    c2.metric("Candidates Analyzed", len(ranked))
    c3.metric("Average Match Score", f"{avg_score}%")
    c4.metric("Top Candidate", top_name)

    st.markdown("### Recent Candidates")
    if candidates:
        df = pd.DataFrame([
            {
                "Candidate": c["name"],
                "Skills": ", ".join(c["extracted_skills"][:6]),
                "Current Match": c.get("match_score", 0),
            }
            for c in candidates
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No resumes uploaded yet.")

elif page == "Create Job Description":
    with st.container(border=True):
        st.subheader("Define the role")
        title = st.text_input("Job title", value=st.session_state.job["title"], placeholder="e.g. Senior Data Scientist")
        description = st.text_area(
            "Job description",
            value=st.session_state.job["description"],
            height=220,
            placeholder="Paste the job description including responsibilities and qualifications...",
        )
        skills_raw = st.text_area(
            "Required skills (comma/newline separated)",
            value=", ".join(st.session_state.job["required_skills"]),
            placeholder="Python, SQL, Machine Learning, NLP",
            height=100,
        )

        if st.button("Save Job Description", type="primary"):
            st.session_state.job = {
                "title": title.strip(),
                "description": description.strip(),
                "required_skills": parse_required_skills(skills_raw),
            }
            st.success("Job profile saved.")

elif page == "Upload Resumes":
    uploads = st.file_uploader("Upload PDF resumes", type=["pdf"], accept_multiple_files=True)

    if uploads and st.button("Process Resumes", type="primary"):
        processed = []
        progress = st.progress(0)
        for idx, file in enumerate(uploads, 1):
            data = file.getvalue()
            text = parse_pdf(data)
            analysis = analyze_resume(text, SKILL_DICTIONARY)
            name = safe_candidate_name(file.name, text)

            record = CandidateRecord(
                name=name,
                resume_text=text,
                cleaned_text=analysis["cleaned_text"],
                extracted_skills=analysis["skills"],
            ).__dict__
            processed.append(record)
            progress.progress(idx / len(uploads))

        st.session_state.candidates = processed
        st.session_state.ranked_candidates = []
        st.success(f"Processed {len(processed)} resumes.")

    if st.session_state.candidates:
        for candidate in st.session_state.candidates:
            with st.expander(candidate["name"], expanded=False):
                c1, c2 = st.columns([1, 2])
                c1.markdown("**Extracted Skills**")
                c1.write(", ".join(candidate["extracted_skills"]) if candidate["extracted_skills"] else "No known skills found")
                c2.markdown("**Resume Preview**")
                st.text_area(
                    f"preview_{candidate['name']}",
                    value=candidate["resume_text"][:1400],
                    height=180,
                    key=f"ta_{candidate['name']}",
                    disabled=True,
                    label_visibility="collapsed",
                )

elif page == "Candidate Ranking":
    job = st.session_state.job
    candidates = st.session_state.candidates

    if not job["description"]:
        st.warning("Please create a job description first.")
    elif not candidates:
        st.warning("Please upload and process resumes first.")
    else:
        if st.button("Run Ranking", type="primary"):
            job_text = preprocess_text(job["description"])
            st.session_state.ranked_candidates = rank_candidates(
                job_text=job_text,
                candidates=candidates,
                required_skills=job["required_skills"],
            )

        ranked = st.session_state.ranked_candidates
        if ranked:
            df = pd.DataFrame([
                {
                    "Candidate Name": c["name"],
                    "Match Score": c["match_score"],
                    "Extracted Skills": ", ".join(c["extracted_skills"]),
                    "Missing Skills": ", ".join(c["missing_skills"]),
                }
                for c in ranked
            ])
            st.dataframe(df, use_container_width=True)

            st.markdown("### Match Progress")
            for c in ranked:
                st.write(f"**{c['name']}** — {c['match_score']}%")
                st.progress(int(c["match_score"]) / 100)

elif page == "Candidate Insights":
    ranked = st.session_state.ranked_candidates

    if not ranked:
        st.info("Run candidate ranking to view insights.")
    else:
        left, right = st.columns([3, 2])
        with left:
            st.subheader("Candidate Comparison")
            comp_df = pd.DataFrame(
                {
                    "Candidate": [c["name"] for c in ranked],
                    "Match Score": [c["match_score"] for c in ranked],
                    "Skill Match %": [c["skill_match_pct"] for c in ranked],
                }
            ).set_index("Candidate")
            st.bar_chart(comp_df)

        with right:
            st.subheader("Skill Frequency")
            all_skills = [skill for c in ranked for skill in c["extracted_skills"]]
            freq = Counter(all_skills)
            if freq:
                sf = pd.DataFrame({"Skill": list(freq.keys()), "Count": list(freq.values())}).set_index("Skill")
                st.bar_chart(sf)
            else:
                st.write("No skills extracted yet.")

        st.markdown("### Candidate-Level Explanations")
        for c in ranked:
            with st.expander(f"{c['name']} — {c['match_score']}%"):
                cols = st.columns(3)
                cols[0].metric("Semantic Similarity", f"{c['semantic_score']}%")
                cols[1].metric("Skill Match", f"{c['skill_match_pct']}%")
                cols[2].metric("Missing Skills", len(c["missing_skills"]))

                st.markdown(f"**Missing Skills:** {', '.join(c['missing_skills']) if c['missing_skills'] else 'None'}")
                st.markdown(f"**Resume Highlights:** {', '.join(c['extracted_skills'][:8]) or 'No highlights found'}")
                st.markdown(
                    "**Match Explanation:** Candidate score blends semantic alignment with required skill coverage. "
                    f"This profile scored {c['semantic_score']}% semantically and {c['skill_match_pct']}% on required skills."
                )
