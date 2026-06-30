"""Match parsed resumes against job requirements."""
from typing import Dict, List

from src.skills import SkillExtractor


class JobMatcher:
    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def match(self, resume: Dict, job_description: str) -> Dict:
        required_skills = self.skill_extractor.extract_skills(job_description)
        candidate_skills = resume.get("skills", [])

        score = self.skill_extractor.get_skill_match_score(required_skills, candidate_skills)
        matched = sorted(set(s.lower() for s in required_skills) & set(s.lower() for s in candidate_skills))
        missing = sorted(set(s.lower() for s in required_skills) - set(s.lower() for s in candidate_skills))

        return {
            "match_score": round(score * 100, 1),
            "matched_skills": matched,
            "missing_skills": missing,
            "required_skills": required_skills,
        }

    def rank_resumes(self, resumes: List[Dict], job_description: str) -> List[Dict]:
        ranked = []
        for resume in resumes:
            result = self.match(resume, job_description)
            ranked.append({**resume, "match": result})
        ranked.sort(key=lambda r: r["match"]["match_score"], reverse=True)
        return ranked
