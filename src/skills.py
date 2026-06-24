"""
🧠 Advanced Skill Extractor
"""

import re
import json
from typing import List, Dict, Set

class SkillExtractor:
    """Advanced skill extraction with categorization"""
    
    def __init__(self):
        self.skills_data = self._load_skills_data()
    
    def _load_skills_data(self) -> Dict:
        """Load skills database"""
        try:
            with open("data/skills.json", "r") as f:
                return json.load(f)
        except:
            return self._get_default_skills()
    
    def _get_default_skills(self) -> Dict:
        """Default skills database"""
        return {
            "programming": {
                "name": "Programming Languages",
                "skills": ["python", "java", "javascript", "c++", "ruby", "php", "c#", "go"]
            },
            "web": {
                "name": "Web Development",
                "skills": ["html", "css", "react", "angular", "vue", "django", "flask"]
            },
            "data": {
                "name": "Data Science",
                "skills": ["sql", "tableau", "power bi", "excel", "r", "pandas", "numpy"]
            },
            "cloud": {
                "name": "Cloud & DevOps",
                "skills": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins"]
            },
            "soft": {
                "name": "Soft Skills",
                "skills": ["communication", "leadership", "problem solving", "teamwork"]
            },
            "security": {
                "name": "Security",
                "skills": ["cybersecurity", "penetration testing", "security", "cryptography"]
            }
        }
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract all skills from text"""
        found_skills = set()
        text_lower = text.lower()
        
        for category in self.skills_data.values():
            for skill in category["skills"]:
                if skill.lower() in text_lower:
                    found_skills.add(skill)
        
        return sorted(list(found_skills))
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills by type"""
        categorized = {}
        
        for category_key, category_data in self.skills_data.items():
            category_skills = []
            for skill in skills:
                if skill.lower() in [s.lower() for s in category_data["skills"]]:
                    category_skills.append(skill)
            
            if category_skills:
                categorized[category_data["name"]] = sorted(category_skills)
        
        return categorized
    
    def get_skill_match_score(self, required_skills: List[str], 
                              candidate_skills: List[str]) -> float:
        """Calculate skill match score"""
        if not required_skills:
            return 1.0
        
        required_set = set(s.lower() for s in required_skills)
        candidate_set = set(s.lower() for s in candidate_skills)
        
        matches = required_set & candidate_set
        return len(matches) / len(required_set)
    