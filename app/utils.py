"""
🛠️ Utility Functions
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

class Utils:
    """Utility functions"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s.,-]', '', text)
        return text.strip()
    
    @staticmethod
    def extract_years(text: str) -> List[str]:
        """Extract years from text"""
        pattern = r'(19|20)\d{2}'
        return re.findall(pattern, text)
    
    @staticmethod
    def calculate_experience_duration(start: str, end: str = "present") -> float:
        """Calculate years of experience"""
        try:
            start_date = datetime.strptime(start, "%Y-%m")
            if end.lower() == "present":
                end_date = datetime.now()
            else:
                end_date = datetime.strptime(end, "%Y-%m")
            
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            return round(months / 12, 1)
        except:
            return 0.0
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number"""
        # Remove non-digits
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone
    
    @staticmethod
    def generate_summary(data: Dict) -> str:
        """Generate a summary from parsed data"""
        parts = []
        
        # Name
        name = data.get('name', 'Candidate')
        parts.append(f"{name} is a professional")
        
        # Experience
        experience = data.get('experience', [])
        if experience:
            titles = [exp.get('title', '') for exp in experience if exp.get('title')]
            if titles:
                parts.append(f"with experience as {', '.join(titles)}")
        
        # Skills
        skills = data.get('skills', [])
        if skills:
            top_skills = ', '.join(skills[:5])
            parts.append(f"skilled in {top_skills}")
        
        # Education
        edu = data.get('education', {})
        if edu.get('degree'):
            parts.append(f"holding a {edu['degree']}")
            if edu.get('institution'):
                parts.append(f"from {edu['institution']}")
        
        summary = ' '.join(parts)
        return summary if summary else "Professional with technical expertise."
