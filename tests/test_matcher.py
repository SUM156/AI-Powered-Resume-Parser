from src.matcher import JobMatcher


def test_match():
    matcher = JobMatcher()
    resume = {"skills": ["python", "sql", "react"]}
    result = matcher.match(resume, "Looking for a Python developer with SQL and AWS experience")
    assert "python" in result["matched_skills"]
    assert "aws" in result["missing_skills"]
    assert 0 <= result["match_score"] <= 100


def test_rank_resumes():
    matcher = JobMatcher()
    resumes = [
        {"name": "A", "skills": ["python", "sql"]},
        {"name": "B", "skills": ["java"]},
    ]
    ranked = matcher.rank_resumes(resumes, "Python and SQL required")
    assert ranked[0]["name"] == "A"
