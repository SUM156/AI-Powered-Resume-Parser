import tempfile

import pytest

from src.database import DatabaseService


@pytest.fixture
def db():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    return DatabaseService(db_path=tmp.name)


def test_save_and_get_resume(db):
    resume_id = db.save_resume({"name": "Jane", "email": "jane@email.com", "skills": ["python"]})
    resume = db.get_resume(resume_id)
    assert resume["name"] == "Jane"
    assert "python" in resume["skills"]


def test_delete_resume(db):
    resume_id = db.save_resume({"name": "Jane", "email": "jane@email.com", "skills": []})
    assert db.delete_resume(resume_id) is True
    assert db.get_resume(resume_id) is None


def test_search_resumes(db):
    db.save_resume({"name": "Alice", "email": "alice@email.com", "skills": ["sql"]})
    results = db.search_resumes("Alice")
    assert len(results) == 1
