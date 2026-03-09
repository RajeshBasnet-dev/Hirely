from __future__ import annotations

from pathlib import Path
import json
import sqlite3
from typing import Any, Iterable


DB_PATH = Path(__file__).parent / "hirely.db"


class HirelyDB:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_tables()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    required_skills TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    resume_text TEXT NOT NULL,
                    cleaned_text TEXT NOT NULL,
                    extracted_skills TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    candidate_id INTEGER NOT NULL,
                    match_score REAL NOT NULL,
                    semantic_score REAL NOT NULL,
                    skill_match_pct REAL NOT NULL,
                    missing_skills TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(job_id) REFERENCES jobs(id),
                    FOREIGN KEY(candidate_id) REFERENCES candidates(id)
                );
                """
            )

    def save_job(self, title: str, description: str, required_skills: Iterable[str]) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO jobs (title, description, required_skills) VALUES (?, ?, ?)",
                (title, description, json.dumps(list(required_skills))),
            )
            return int(cur.lastrowid)

    def get_latest_job(self) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT 1").fetchone()
            if not row:
                return None
            out = dict(row)
            out["required_skills"] = json.loads(out["required_skills"])
            return out

    def replace_candidates(self, candidates: list[dict[str, Any]]) -> list[int]:
        with self._connect() as conn:
            conn.execute("DELETE FROM candidates")
            ids = []
            for c in candidates:
                cur = conn.execute(
                    """
                    INSERT INTO candidates (name, resume_text, cleaned_text, extracted_skills)
                    VALUES (?, ?, ?, ?)
                    """,
                    (c["name"], c["resume_text"], c["cleaned_text"], json.dumps(c["extracted_skills"])),
                )
                ids.append(int(cur.lastrowid))
            return ids

    def load_candidates(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM candidates ORDER BY id ASC").fetchall()
        output = []
        for row in rows:
            c = dict(row)
            c["extracted_skills"] = json.loads(c["extracted_skills"])
            output.append(c)
        return output

    def save_results(self, job_id: int, ranked_candidates: list[dict[str, Any]]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM results")
            for c in ranked_candidates:
                conn.execute(
                    """
                    INSERT INTO results (job_id, candidate_id, match_score, semantic_score, skill_match_pct, missing_skills)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job_id,
                        c.get("id", -1),
                        c["match_score"],
                        c["semantic_score"],
                        c["skill_match_pct"],
                        json.dumps(c["missing_skills"]),
                    ),
                )

    def load_results(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT r.match_score, r.semantic_score, r.skill_match_pct, r.missing_skills,
                       c.id as candidate_id, c.name, c.resume_text, c.cleaned_text, c.extracted_skills
                FROM results r
                JOIN candidates c ON c.id = r.candidate_id
                ORDER BY r.match_score DESC
                """
            ).fetchall()

        output = []
        for row in rows:
            r = dict(row)
            r["missing_skills"] = json.loads(r["missing_skills"])
            r["extracted_skills"] = json.loads(r["extracted_skills"])
            r["id"] = r.pop("candidate_id")
            output.append(r)
        return output
