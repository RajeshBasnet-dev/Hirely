from __future__ import annotations

from dataclasses import asdict
from collections import Counter

import altair as alt
import pandas as pd
import streamlit as st

from database import HirelyDB
from ml_pipeline import analyze_resume, preprocess_text, rank_candidates
from resume_parser import parse_pdf
from theme import THEMES, inject_css
from utils import CandidateRecord, SKILL_DICTIONARY, parse_required_skills, safe_candidate_name


st.set_page_config(page_title="Hirely — AI Resume Screening", page_icon="🧠", layout="wide")

db = HirelyDB()

if "job" not in st.session_state:
    latest_job = db.get_latest_job()
    st.session_state.job = {
        "title": latest_job["title"] if latest_job else "",
        "description": latest_job["description"] if latest_job else "",
        "required_skills": latest_job["required_skills"] if latest_job else [],
        "id": latest_job["id"] if latest_job else None,
    }
if "candidates" not in st.session_state:
    st.session_state.candidates = db.load_candidates()
if "ranked_candidates" not in st.session_state:
    st.session_state.ranked_candidates = db.load_results()
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

st.markdown(inject_css(THEMES[st.session_state.theme]), unsafe_allow_html=True)


def render_header(page_name: str) -> None:
    st.markdown(
        f"""
        <div class='hirely-shell'>
            <p class='hirely-logo'>Hirely AI • Resume Intelligence Cloud</p>
            <p class='hirely-subtitle'>Modern screening workflow: Upload → Parse → Rank → Insights</p>
            <span class='hirely-pill'>{page_name}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class='hirely-card'>
            <p class='hirely-kpi-label'>{label}</p>
            <p class='hirely-kpi-value'>{value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("### 🧠 Hirely")
    st.caption("Investor-ready AI hiring dashboard")
    st.session_state.theme = st.toggle("Light mode", value=st.session_state.theme == "Light") and "Light" or "Dark"
    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "1) Upload & Parse",
            "2) Job Requirements",
            "3) Rank Candidates",
            "4) Results & Exports",
        ],
    )
    st.markdown("---")
    st.caption(f"Skills in taxonomy: {len(SKILL_DICTIONARY)}")

render_header(page)

if page == "Dashboard":
    candidates = st.session_state.candidates
    ranked = st.session_state.ranked_candidates

    total = len(candidates)
    analyzed = len(ranked)
    avg_score = round(sum(c.get("match_score", 0) for c in ranked) / analyzed, 1) if analyzed else 0
    top_candidate = ranked[0]["name"] if ranked else "—"

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Total Candidates", str(total))
    with m2:
        metric_card("Profiles Ranked", str(analyzed))
    with m3:
        metric_card("Average Match", f"{avg_score}%")
    with m4:
        metric_card("Top Candidate", top_candidate)

    if ranked:
        st.markdown("### Candidate Scoreboard")
        ranking_df = pd.DataFrame(ranked)
        chart = (
            alt.Chart(ranking_df)
            .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
            .encode(
                x=alt.X("name:N", sort="-y", title="Candidate"),
                y=alt.Y("match_score:Q", title="Match %"),
                color=alt.Color("match_score:Q", scale=alt.Scale(scheme="blues")),
                tooltip=["name", "match_score", "semantic_score", "skill_match_pct"],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, use_container_width=True)

        st.markdown("### Skill Coverage")
        top_skills = Counter(skill for c in ranked for skill in c["extracted_skills"]).most_common(10)
        if top_skills:
            skill_df = pd.DataFrame(top_skills, columns=["skill", "count"])
            st.altair_chart(
                alt.Chart(skill_df)
                .mark_bar(cornerRadius=6)
                .encode(x="count:Q", y=alt.Y("skill:N", sort="-x"), color=alt.value(THEMES[st.session_state.theme].secondary)),
                use_container_width=True,
            )

        heat_df = ranking_df[["name", "semantic_score", "skill_match_pct", "match_score"]].melt(
            id_vars="name", var_name="metric", value_name="score"
        )
        st.markdown("### Match Heatmap")
        heat = (
            alt.Chart(heat_df)
            .mark_rect(cornerRadius=4)
            .encode(
                x=alt.X("metric:N", title=None),
                y=alt.Y("name:N", title=None),
                color=alt.Color("score:Q", scale=alt.Scale(scheme="teals")),
                tooltip=["name", "metric", "score"],
            )
            .properties(height=260)
        )
        st.altair_chart(heat, use_container_width=True)
    else:
        st.info("Start by uploading resumes and running ranking to populate the SaaS dashboard.")

elif page == "1) Upload & Parse":
    st.subheader("Step 1: Upload resumes")
    uploads = st.file_uploader("Drag and drop PDF resumes", type=["pdf"], accept_multiple_files=True)

    if uploads and st.button("Parse Uploaded Resumes", type="primary"):
        processed = []
        progress = st.progress(0)
        for idx, file in enumerate(uploads, 1):
            text = parse_pdf(file.getvalue())
            analysis = analyze_resume(text, SKILL_DICTIONARY)
            record = CandidateRecord(
                name=safe_candidate_name(file.name, text),
                resume_text=text,
                cleaned_text=analysis["cleaned_text"],
                extracted_skills=analysis["skills"],
            )
            processed.append(asdict(record))
            progress.progress(idx / len(uploads), text=f"Parsing {file.name}")

        ids = db.replace_candidates(processed)
        for idx, cid in enumerate(ids):
            processed[idx]["id"] = cid

        st.session_state.candidates = processed
        st.session_state.ranked_candidates = []
        st.success(f"Parsed {len(processed)} resumes. Move to Step 2.")

    if st.session_state.candidates:
        st.markdown("### Parsed candidate cards")
        for candidate in st.session_state.candidates:
            with st.expander(f"{candidate['name']} • {len(candidate['extracted_skills'])} skills", expanded=False):
                c1, c2 = st.columns([1, 2])
                c1.markdown("**Top extracted skills**")
                c1.write(", ".join(candidate["extracted_skills"][:12]) if candidate["extracted_skills"] else "No known skills")
                c2.markdown("**Resume snippet**")
                st.text_area(
                    "Resume preview",
                    value=candidate["resume_text"][:1500],
                    key=f"preview_{candidate['name']}",
                    disabled=True,
                    height=180,
                    label_visibility="collapsed",
                )

elif page == "2) Job Requirements":
    st.subheader("Step 2: Define the target role")
    title = st.text_input("Job title", value=st.session_state.job["title"], placeholder="Senior Data Scientist")
    description = st.text_area(
        "Job description",
        value=st.session_state.job["description"],
        height=240,
        placeholder="Paste responsibilities, preferred qualifications, and required domain experience.",
    )
    skills_raw = st.text_area(
        "Required skills",
        value=", ".join(st.session_state.job["required_skills"]),
        placeholder="Python, NLP, SQL, MLOps, Experimentation",
        height=110,
    )

    if st.button("Save role profile", type="primary"):
        required_skills = parse_required_skills(skills_raw)
        job_id = db.save_job(title.strip(), description.strip(), required_skills)
        st.session_state.job = {
            "title": title.strip(),
            "description": description.strip(),
            "required_skills": required_skills,
            "id": job_id,
        }
        st.success("Role profile saved. Move to Step 3 for ranking.")

elif page == "3) Rank Candidates":
    job = st.session_state.job
    candidates = st.session_state.candidates

    st.subheader("Step 3: AI ranking")
    if not job["description"]:
        st.warning("Add a job description in Step 2 first.")
    elif not candidates:
        st.warning("Upload and parse resumes in Step 1 first.")
    else:
        if st.button("Run AI Ranking", type="primary"):
            ranked = rank_candidates(
                job_text=preprocess_text(job["description"]),
                candidates=candidates,
                required_skills=job["required_skills"],
            )
            st.session_state.ranked_candidates = ranked
            if job.get("id"):
                db.save_results(job_id=job["id"], ranked_candidates=ranked)

        ranked = st.session_state.ranked_candidates
        if ranked:
            st.success("Ranking completed.")
            for item in ranked:
                st.markdown(f"**{item['name']}**")
                st.progress(item["match_score"] / 100, text=f"Overall match {item['match_score']}%")

elif page == "4) Results & Exports":
    st.subheader("Step 4: Review, filter, and export")
    ranked = st.session_state.ranked_candidates

    if not ranked:
        st.info("Run ranking in Step 3 to unlock insights and export actions.")
    else:
        df = pd.DataFrame(ranked)
        max_score = int(df["match_score"].max())
        score_filter = st.slider("Minimum match score", min_value=0, max_value=100, value=min(65, max_score))
        skill_filter = st.text_input("Filter by skill keyword", placeholder="python / sql / leadership")
        title_filter = st.text_input("Filter by job-title text in resume", placeholder="data scientist")

        filtered = df[df["match_score"] >= score_filter]
        if skill_filter:
            needle = skill_filter.lower().strip()
            filtered = filtered[filtered["extracted_skills"].apply(lambda skills: any(needle in s.lower() for s in skills))]
        if title_filter:
            tneedle = title_filter.lower().strip()
            filtered = filtered[filtered["resume_text"].str.lower().str.contains(tneedle, na=False)]

        sort_col = st.selectbox("Sort table by", ["match_score", "semantic_score", "skill_match_pct", "name"])
        ascending = st.toggle("Ascending sort", value=False)
        filtered = filtered.sort_values(by=sort_col, ascending=ascending)

        table_df = filtered[["name", "match_score", "semantic_score", "skill_match_pct", "missing_skills", "extracted_skills"]].copy()
        table_df.columns = ["Candidate", "Match %", "Semantic %", "Skill Match %", "Missing Skills", "Top Skills"]
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        st.download_button(
            "Download filtered candidates (CSV)",
            data=table_df.to_csv(index=False).encode("utf-8"),
            file_name="hirely_top_candidates.csv",
            mime="text/csv",
            type="primary",
        )

        st.markdown("### Candidate skill alignment (radar-style)")
        required = st.session_state.job.get("required_skills", [])[:8]
        if required:
            radar_rows = []
            top_n = filtered.head(3)
            for _, row in top_n.iterrows():
                candidate_skills = {s.lower() for s in row["extracted_skills"]}
                for skill in required:
                    radar_rows.append(
                        {
                            "candidate": row["name"],
                            "skill": skill,
                            "score": 100 if skill.lower() in candidate_skills else 25,
                        }
                    )
            radar_df = pd.DataFrame(radar_rows)
            radar = (
                alt.Chart(radar_df)
                .mark_line(point=True)
                .encode(
                    theta=alt.Theta("skill:N", sort=required),
                    radius=alt.Radius("score:Q", scale=alt.Scale(domain=[0, 100])),
                    color="candidate:N",
                    tooltip=["candidate", "skill", "score"],
                )
                .properties(height=420)
            )
            st.altair_chart(radar, use_container_width=True)
        else:
            st.caption("Add required skills in Step 2 to generate radar alignment.")

st.markdown("<div class='hirely-footer'>Hirely • AI Resume Screening Platform • Built for recruiters and hiring teams</div>", unsafe_allow_html=True)
