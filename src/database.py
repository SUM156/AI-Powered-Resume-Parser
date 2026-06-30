"""Lightweight SQLite-backed database service (no external deps required)."""
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from src import config


class DatabaseService:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(config.DATA_DIR / "resumes.db")
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    skills TEXT,
                    experience TEXT,
                    education TEXT,
                    filename TEXT,
                    parsed_at TEXT
                )
                """
            )

    def save_resume(self, data: Dict) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO resumes (name, email, phone, skills, experience, education, filename, parsed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get("name", "Unknown"),
                    data.get("email", ""),
                    data.get("phone", ""),
                    json.dumps(data.get("skills", [])),
                    json.dumps(data.get("experience", [])),
                    json.dumps(data.get("education", {})),
                    data.get("filename", ""),
                    datetime.utcnow().isoformat(),
                ),
            )
            return cursor.lastrowid

    def get_resume(self, resume_id: int) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,)).fetchone()
            return self._row_to_dict(row) if row else None

    def get_resumes(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM resumes ORDER BY parsed_at DESC LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def search_resumes(self, query: str) -> List[Dict]:
        like = f"%{query}%"
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM resumes WHERE name LIKE ? OR email LIKE ? OR skills LIKE ?",
                (like, like, like),
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def delete_resume(self, resume_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            return cursor.rowcount > 0

    def get_analytics(self) -> Dict:
        from collections import Counter

        with self._connect() as conn:
            rows = conn.execute("SELECT skills FROM resumes").fetchall()
        all_skills = []
        for row in rows:
            all_skills.extend(json.loads(row["skills"] or "[]"))
        top_skills = Counter(all_skills).most_common(10)
        return {
            "total_resumes": len(rows),
            "total_unique_skills": len(set(all_skills)),
            "top_skills": [{"skill": s, "count": c} for s, c in top_skills],
        }

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
            "skills": json.loads(row["skills"] or "[]"),
            "experience": json.loads(row["experience"] or "[]"),
            "education": json.loads(row["education"] or "{}"),
            "filename": row["filename"],
            "parsed_at": row["parsed_at"],
        }
