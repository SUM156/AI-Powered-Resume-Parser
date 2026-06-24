"""
⚙️ Configuration Module
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Application settings
    APP_NAME = "AI Resume Parser"
    APP_VERSION = "4.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    ASSETS_DIR = BASE_DIR / "assets"
    EXPORTS_DIR = BASE_DIR / "exports"
    
    # Data files
    SKILLS_FILE = DATA_DIR / "skills.json"
    EDUCATION_FILE = DATA_DIR / "education.json"
    COMPANIES_FILE = DATA_DIR / "companies.json"
    
    # Parser settings
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.75))
    MAX_SKILLS = int(os.getenv("MAX_SKILLS", 25))
    
    # Export settings
    DEFAULT_EXPORT_FORMAT = os.getenv("DEFAULT_EXPORT_FORMAT", "json")
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/resumes.db")
    
    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SESSION_EXPIRY = int(os.getenv("SESSION_EXPIRY", 3600))
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        for directory in [cls.DATA_DIR, cls.ASSETS_DIR, cls.EXPORTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_skill_categories(cls) -> list:
        """Get skill categories"""
        return [
            "Programming Languages",
            "Web Development",
            "Data Science & AI",
            "Cloud & DevOps",
            "Databases",
            "Soft Skills",
            "Security",
            "Project Management",
            "Languages",
            "Certifications"
        ]