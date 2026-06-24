"""
📄 Resume Parser Core Module
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
import pdfplumber
from docx import Document

class ResumeParser:
    """Core resume parsing functionality"""
    
    def __init__(self):
        self.skills_db = self._load_skills_db()
        self.education_db = self._load_education_db()
    
    def _load_skills_db(self) -> Dict:
        """Load skills database"""
        try:
            with open("data/skills.json", "r") as f:
                return json.load(f)
        except:
            return self._get_default_skills()
    
    def _load_education_db(self) -> Dict:
        """Load education database"""
        try:
            with open("data/education.json", "r") as f:
                return json.load(f)
        except:
            return self._get_default_education()
    
    def _get_default_skills(self) -> Dict:
        """Default skills database"""
        return {
            "programming": ["python", "java", "javascript", "c++", "ruby", "php"],
            "web": ["html", "css", "react", "angular", "vue", "django"],
            "data": ["sql", "tableau", "power bi", "excel", "r", "pandas"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
            "soft": ["communication", "leadership", "problem solving", "teamwork"]
        }
    
    def _get_default_education(self) -> Dict:
        """Default education database"""
        return {
            "degrees": {
                "bachelor": ["b.s.", "b.a.", "b.eng", "b.tech"],
                "master": ["m.s.", "m.a.", "m.eng", "m.b.a."],
                "phd": ["ph.d.", "phd", "doctorate"]
            }
        }
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume from file"""
        text = self._extract_text(file_path)
        return {
            "name": self._extract_name(text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "skills": self._extract_skills(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "summary": self._extract_summary(text)
        }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from file"""
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext == ".docx":
            return self._extract_docx(file_path)
        elif ext == ".txt":
            return self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            # Try pdfplumber first (better for tables)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        return text
    
    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def _extract_txt(self, file_path: Path) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_name(self, text: str) -> str:
        """Extract name from text"""
        # Simple name extraction - look for common patterns
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if len(line.strip()) > 0 and len(line.split()) <= 4:
                # Assume first non-empty line with 2-4 words is name
                if any(c.isupper() for c in line):
                    return line.strip()
        return "Unknown"
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        # US phone number patterns
        patterns = [
            r'\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}',
            r'\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}',
            r'[0-9]{3}-[0-9]{3}-[0-9]{4}',
            r'[0-9]{10}'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        found_skills = set()
        text_lower = text.lower()
        
        for category, skills in self.skills_db.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.add(skill)
        
        return sorted(list(found_skills))
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract experience from text"""
        experiences = []
        lines = text.split('\n')
        
        # Look for common experience patterns
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['experience', 'employment', 'work']):
                # Collect context
                context = []
                for j in range(i, min(i + 10, len(lines))):
                    if lines[j].strip():
                        context.append(lines[j].strip())
                
                if context:
                    # Try to parse job details
                    exp = {
                        "company": "Unknown",
                        "title": "Unknown",
                        "duration": "Unknown",
                        "description": " ".join(context[:3])
                    }
                    
                    # Look for company names (capitalized words)
                    for part in context:
                        words = part.split()
                        if len(words) > 1:
                            # Check if it looks like a company name
                            if all(w[0].isupper() for w in words if len(w) > 2):
                                exp["company"] = " ".join(words[:3])
                                break
                    
                    experiences.append(exp)
        
        return experiences
    
    def _extract_education(self, text: str) -> Dict:
        """Extract education from text"""
        education = {
            "degree": "Unknown",
            "institution": "Unknown",
            "year": "Unknown"
        }
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for degree
            for level, degrees in self.education_db["degrees"].items():
                for degree in degrees:
                    if degree in line_lower:
                        education["degree"] = line.strip()
                        
                        # Try to get institution (look in nearby lines)
                        if i > 0 and len(lines[i-1].strip()) > 0:
                            education["institution"] = lines[i-1].strip()
                        elif i < len(lines) - 1:
                            education["institution"] = lines[i+1].strip()
                        
                        # Try to find year
                        year_match = re.search(r'(19|20)\d{2}', line)
                        if year_match:
                            education["year"] = year_match.group(0)
                        
                        return education
        
        return education
    
    def _extract_summary(self, text: str) -> str:
        """Extract summary/profile from text"""
        lines = text.split('\n')
        
        # Look for profile/summary section
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['profile', 'summary', 'objective']):
                summary = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip():
                        summary.append(lines[j].strip())
                return " ".join(summary[:3])
        
        # Fallback: first paragraph
        for line in lines[:20]:
            if len(line.strip()) > 50:
                return line.strip()
        
        return "No summary available"
    
    def batch_process(self, directory: str) -> List[Dict]:
        """Process multiple resumes in directory"""
        results = []
        path = Path(directory)
        
        for file_path in path.glob('*'):
            if file_path.suffix.lower() in ['.pdf', '.docx', '.txt']:
                try:
                    result = self.parse_resume(str(file_path))
                    result['filename'] = file_path.name
                    results.append(result)
                except Exception as e:
                    print(f"Error parsing {file_path.name}: {e}")
        
        return results
