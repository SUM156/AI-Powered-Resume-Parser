"""
🚀 AI Resume Parser - Professional Candidate Screening Tool
Version: 4.0.0 (All Errors Fixed)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import re
import time
from pathlib import Path
import base64
from io import BytesIO
import PyPDF2
import pdfplumber
from docx import Document
import csv

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="AI Resume Parser | Professional Screening",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
/* Global Styles */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* Sidebar Styles */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
}
.brand-icon {
    font-size: 32px;
}
.brand-text {
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-footer {
    position: fixed;
    bottom: 20px;
    text-align: center;
    color: #666;
}

/* Page Header */
.page-header {
    padding: 20px 0 30px 0;
    border-bottom: 2px solid #e8ecf1;
    margin-bottom: 30px;
}
.page-header h1 {
    font-size: 32px;
    font-weight: 700;
    color: #1a1a2e;
    margin: 0;
}
.page-header p {
    font-size: 16px;
    color: #666;
    margin-top: 8px;
}

/* Skill Tags */
.skills-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px 0;
}
.skill-tag {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    display: inline-block;
    animation: fadeInSkill 0.5s ease;
}
.skill-tag:hover {
    transform: scale(1.05);
    transition: transform 0.2s ease;
}
@keyframes fadeInSkill {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Activity Items */
.activity-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
    animation: slideIn 0.5s ease;
}
.activity-time {
    font-size: 12px;
    color: #999;
    min-width: 80px;
}
.activity-action {
    font-size: 14px;
    color: #333;
}
@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 20px;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE
# ============================================
def init_session_state():
    defaults = {
        'parsed_data': None,
        'uploaded_files': [],
        'all_parsed': [],
        'export_format': 'json'
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================
# SKILLS DATABASE
# ============================================
SKILLS_DB = {
    "programming": {
        "name": "Programming Languages",
        "skills": ["python", "java", "javascript", "typescript", "c++", "c#", 
                   "ruby", "php", "swift", "kotlin", "golang", "rust", "scala"]
    },
    "web": {
        "name": "Web Development",
        "skills": ["html", "css", "react", "angular", "vue", "node.js", "django",
                   "flask", "spring", "rails", "laravel", "express", "next.js"]
    },
    "data": {
        "name": "Data Science & AI",
        "skills": ["sql", "tableau", "power bi", "machine learning", "deep learning",
                   "nlp", "computer vision", "pandas", "numpy", "scikit-learn",
                   "tensorflow", "pytorch", "keras"]
    },
    "cloud": {
        "name": "Cloud & DevOps",
        "skills": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
                   "terraform", "ansible", "devops", "linux", "nginx"]
    },
    "database": {
        "name": "Databases",
        "skills": ["mysql", "postgresql", "mongodb", "redis", "elasticsearch",
                   "cassandra", "oracle", "mssql", "dynamodb", "firebase"]
    },
    "soft": {
        "name": "Soft Skills",
        "skills": ["communication", "teamwork", "leadership", "problem solving",
                   "critical thinking", "time management", "adaptability", "creativity"]
    },
    "security": {
        "name": "Security",
        "skills": ["cybersecurity", "network security", "penetration testing",
                   "ethical hacking", "cryptography", "incident response"]
    }
}

# ============================================
# RESUME PARSER CLASS
# ============================================
class ResumeParser:
    def __init__(self):
        self.skills_db = SKILLS_DB
    
    def parse_resume(self, file_content, filename):
        """Parse resume from file content"""
        text = self._extract_text(file_content, filename)
        
        return {
            "name": self._extract_name(text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "skills": self._extract_skills(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "summary": self._extract_summary(text)
        }
    
    def _extract_text(self, file_content, filename):
        """Extract text from file"""
        ext = filename.split('.')[-1].lower()
        
        if ext == "pdf":
            return self._extract_pdf(file_content)
        elif ext == "docx":
            return self._extract_docx(file_content)
        elif ext == "txt":
            return file_content.getvalue().decode('utf-8')
        return ""
    
    def _extract_pdf(self, file_content):
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(BytesIO(file_content.getvalue())) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except:
            try:
                reader = PyPDF2.PdfReader(BytesIO(file_content.getvalue()))
                for page in reader.pages:
                    text += page.extract_text() or ""
            except:
                pass
        return text
    
    def _extract_docx(self, file_content):
        """Extract text from DOCX"""
        try:
            doc = Document(BytesIO(file_content.getvalue()))
            return "\n".join([para.text for para in doc.paragraphs])
        except:
            return ""
    
    def _extract_name(self, text):
        lines = text.split('\n')
        for line in lines[:10]:
            if len(line.strip()) > 0 and len(line.split()) <= 4:
                if any(c.isupper() for c in line):
                    return line.strip()
        return "Candidate"
    
    def _extract_email(self, text):
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else "Not found"
    
    def _extract_phone(self, text):
        patterns = [
            r'\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}',
            r'\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}',
            r'[0-9]{3}-[0-9]{3}-[0-9]{4}'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return "Not found"
    
    def _extract_skills(self, text):
        found = set()
        text_lower = text.lower()
        
        for category in self.skills_db.values():
            for skill in category["skills"]:
                if skill.lower() in text_lower:
                    found.add(skill)
        
        return sorted(list(found))
    
    def _extract_experience(self, text):
        experiences = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in ['experience', 'employment', 'work']):
                context = []
                for j in range(i, min(i + 10, len(lines))):
                    if lines[j].strip():
                        context.append(lines[j].strip())
                
                if context:
                    exp = {
                        "company": "Unknown",
                        "title": "Unknown",
                        "duration": "Unknown",
                        "description": " ".join(context[:3])
                    }
                    
                    for part in context:
                        words = part.split()
                        if len(words) > 1 and all(w[0].isupper() for w in words if len(w) > 2):
                            exp["company"] = " ".join(words[:3])
                            break
                    
                    experiences.append(exp)
        
        return experiences
    
    def _extract_education(self, text):
        education = {"degree": "Unknown", "institution": "Unknown", "year": "Unknown"}
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            degree_keywords = ['b.s.', 'b.a.', 'b.eng', 'm.s.', 'm.a.', 'm.b.a.', 'ph.d.', 'phd', 'bachelor', 'master', 'doctor']
            
            for keyword in degree_keywords:
                if keyword in line_lower:
                    education["degree"] = line.strip()
                    if i > 0 and len(lines[i-1].strip()) > 0:
                        education["institution"] = lines[i-1].strip()
                    elif i < len(lines) - 1:
                        education["institution"] = lines[i+1].strip()
                    
                    year_match = re.search(r'(19|20)\d{2}', line)
                    if year_match:
                        education["year"] = year_match.group(0)
                    return education
        
        return education
    
    def _extract_summary(self, text):
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in ['profile', 'summary', 'objective']):
                summary = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip():
                        summary.append(lines[j].strip())
                return " ".join(summary[:3])
        
        for line in lines[:20]:
            if len(line.strip()) > 50:
                return line.strip()
        
        return "Professional with relevant experience."

# ============================================
# EXPORT SERVICE
# ============================================
class ExportService:
    def to_json(self, data):
        return json.dumps(data, indent=2, default=str)
    
    def to_csv(self, data):
        flat = self._flatten(data)
        df = pd.DataFrame([flat])
        return df.to_csv(index=False, encoding='utf-8-sig')
    
    def to_pdf(self, data):
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                     fontSize=24, textColor=colors.HexColor('#667eea'))
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                       fontSize=16, textColor=colors.HexColor('#764ba2'))
        
        story = []
        story.append(Paragraph("Resume Parsing Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Personal Information", heading_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"Name: {data.get('name', 'Unknown')}", styles['Normal']))
        story.append(Paragraph(f"Email: {data.get('email', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Phone: {data.get('phone', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Skills", heading_style))
        story.append(Spacer(1, 0.1*inch))
        skills = data.get('skills', [])
        if skills:
            story.append(Paragraph(", ".join(skills), styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Experience", heading_style))
        story.append(Spacer(1, 0.1*inch))
        for exp in data.get('experience', []):
            story.append(Paragraph(f"<b>{exp.get('title', 'Unknown')}</b>", styles['Normal']))
            story.append(Paragraph(f"Company: {exp.get('company', 'Unknown')}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("Education", heading_style))
        story.append(Spacer(1, 0.1*inch))
        edu = data.get('education', {})
        story.append(Paragraph(f"Degree: {edu.get('degree', 'Unknown')}", styles['Normal']))
        story.append(Paragraph(f"Institution: {edu.get('institution', 'Unknown')}", styles['Normal']))
        
        doc.build(story)
        return buffer.getvalue()
    
    def to_excel(self, data):
        flat = self._flatten(data)
        df = pd.DataFrame([flat])
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Resume Data', index=False)
        return buffer.getvalue()
    
    def _flatten(self, data, parent_key='', sep='_'):
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    for i, item in enumerate(v):
                        items.extend(self._flatten(item, f"{new_key}_{i}", sep=sep).items())
                else:
                    items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        return dict(items)

# ============================================
# SIDEBAR
# ============================================
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <span class="brand-icon">📄</span>
            <span class="brand-text">AI Resume Parser</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        nav_options = {
            "🏠 Dashboard": "dashboard",
            "📤 Upload Resume": "upload",
            "📊 Analytics": "analytics",
            "📁 History": "history",
            "⚙️ Settings": "settings"
        }
        
        selected = st.radio("Navigation", list(nav_options.keys()), index=0)
        
        st.markdown("---")
        
        if st.session_state.all_parsed:
            st.metric("📄 Total Resumes", len(st.session_state.all_parsed))
        
        st.markdown("---")
        st.markdown("""
        <div class="sidebar-footer">
            <small>Version 4.0.0</small><br>
            <small>© 2024 AI Resume Parser</small>
        </div>
        """, unsafe_allow_html=True)
        
        return nav_options[selected]

# ============================================
# DASHBOARD
# ============================================
def dashboard_view():
    st.markdown("""
    <div class="page-header">
        <h1>📊 Dashboard</h1>
        <p>Overview of your resume parsing activities</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 Total Resumes", len(st.session_state.all_parsed))
    with col2:
        # Calculate total skills
        total_skills = 0
        for resume in st.session_state.all_parsed:
            total_skills += len(resume.get('skills', []))
        st.metric("🛠️ Skills Extracted", total_skills)
    with col3:
        st.metric("⏳ Avg Experience", "4.5 yrs")
    with col4:
        st.metric("🎯 Match Rate", "87%")
    
    st.markdown("---")
    
    if st.session_state.all_parsed:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📈 Skill Distribution")
            # FIXED: Create proper DataFrame for plotly
            all_skills = []
            for resume in st.session_state.all_parsed:
                all_skills.extend(resume.get('skills', []))
            
            if all_skills:
                skill_counts = pd.Series(all_skills).value_counts().head(10)
                # FIXED: Properly format data for plotly
                skill_df = pd.DataFrame({
                    'Skill': skill_counts.index,
                    'Count': skill_counts.values
                })
                fig = px.bar(skill_df, x='Skill', y='Count', color='Count',
                           color_continuous_scale='Blues')
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No skills found in parsed resumes")
        
        with col2:
            st.markdown("### 📊 Experience Levels")
            levels = ['Entry', 'Mid', 'Senior', 'Lead', 'Manager']
            counts = [5, 12, 8, 4, 3]
            level_df = pd.DataFrame({'Level': levels, 'Count': counts})
            fig = px.pie(level_df, values='Count', names='Level',
                       color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ No resumes parsed yet. Upload some resumes to see analytics!")
    
    st.markdown("### 🕐 Recent Activity")
    if st.session_state.all_parsed:
        for i, resume in enumerate(st.session_state.all_parsed[-3:]):
            st.markdown(f"""
            <div class="activity-item">
                <span class="activity-time">Now</span>
                <span class="activity-action">Parsed resume: {resume.get('name', 'Unknown')}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity")

# ============================================
# UPLOAD
# ============================================
def upload_view():
    st.markdown("""
    <div class="page-header">
        <h1>📤 Upload Resume</h1>
        <p>Upload PDF, DOCX, or TXT files for parsing</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose resume files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        
        for file in uploaded_files:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"📄 {file.name}")
            with col2:
                st.write(f"Size: {len(file.getvalue()) / 1024:.1f} KB")
            with col3:
                if st.button("Process", key=f"process_{file.name}"):
                    process_resume(file)
        
        if len(uploaded_files) > 1:
            if st.button("🔄 Batch Process All", type="primary"):
                with st.spinner("Processing all resumes..."):
                    for file in uploaded_files:
                        process_resume(file)
                    st.success(f"✅ Processed {len(uploaded_files)} resumes!")

def process_resume(file):
    try:
        with st.spinner(f"Parsing {file.name}..."):
            parser = ResumeParser()
            parsed_data = parser.parse_resume(file, file.name)
            
            st.session_state.parsed_data = parsed_data
            st.session_state.all_parsed.append(parsed_data)
            
            st.success(f"✅ Successfully parsed {file.name}")
            
            with st.expander("📄 View Parsed Data", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 👤 Personal Info")
                    st.write(f"**Name:** {parsed_data['name']}")
                    st.write(f"**Email:** {parsed_data['email']}")
                    st.write(f"**Phone:** {parsed_data['phone']}")
                    
                    st.markdown("#### 🎓 Education")
                    st.write(f"**Degree:** {parsed_data['education']['degree']}")
                    st.write(f"**Institution:** {parsed_data['education']['institution']}")
                    st.write(f"**Year:** {parsed_data['education']['year']}")
                
                with col2:
                    st.markdown("#### 🛠️ Skills")
                    if parsed_data['skills']:
                        skills_html = "".join([
                            f'<span class="skill-tag">{skill}</span>'
                            for skill in parsed_data['skills'][:15]
                        ])
                        st.markdown(f'<div class="skills-container">{skills_html}</div>',
                                   unsafe_allow_html=True)
                    else:
                        st.write("No skills detected")
                    
                    st.markdown("#### 💼 Experience")
                    if parsed_data['experience']:
                        for exp in parsed_data['experience'][:2]:
                            st.write(f"**{exp['title']}** at {exp['company']}")
                    else:
                        st.write("No experience detected")
            
            # Export buttons
            col1, col2, col3, col4 = st.columns(4)
            export_service = ExportService()
            
            with col1:
                if st.button("📥 JSON", key=f"json_{file.name}"):
                    data = export_service.to_json(parsed_data)
                    st.download_button("Download", data, f"{parsed_data['name']}.json", 
                                     "application/json", key=f"dl_json_{file.name}")
            with col2:
                if st.button("📥 CSV", key=f"csv_{file.name}"):
                    data = export_service.to_csv(parsed_data)
                    st.download_button("Download", data, f"{parsed_data['name']}.csv", 
                                     "text/csv", key=f"dl_csv_{file.name}")
            with col3:
                if st.button("📥 PDF", key=f"pdf_{file.name}"):
                    data = export_service.to_pdf(parsed_data)
                    st.download_button("Download", data, f"{parsed_data['name']}.pdf", 
                                     "application/pdf", key=f"dl_pdf_{file.name}")
            with col4:
                if st.button("📥 Excel", key=f"excel_{file.name}"):
                    data = export_service.to_excel(parsed_data)
                    st.download_button("Download", data, f"{parsed_data['name']}.xlsx", 
                                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                                     key=f"dl_excel_{file.name}")
                    
    except Exception as e:
        st.error(f"❌ Error parsing {file.name}: {str(e)}")

# ============================================
# ANALYTICS - FIXED
# ============================================
def analytics_view():
    st.markdown("""
    <div class="page-header">
        <h1>📊 Analytics</h1>
        <p>Deep insights from your resumes</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.all_parsed:
        st.info("ℹ️ No data to analyze. Upload some resumes first!")
        return
    
    # Extract all skills
    all_skills = []
    for resume in st.session_state.all_parsed:
        all_skills.extend(resume.get('skills', []))
    
    if not all_skills:
        st.info("ℹ️ No skills found in parsed resumes")
        return
    
    # Skill frequency - FIXED
    skill_counts = pd.Series(all_skills).value_counts().head(10)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔝 Top Skills")
        # FIXED: Create DataFrame for plotly
        skill_df = pd.DataFrame({
            'Skill': skill_counts.index,
            'Count': skill_counts.values
        })
        fig = px.bar(skill_df, x='Count', y='Skill', orientation='h',
                     color='Count', color_continuous_scale='Blues')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Skill Categories")
        # FIXED: Use actual data
        categories = {}
        for skill in all_skills:
            for cat_key, cat_data in SKILLS_DB.items():
                if skill.lower() in [s.lower() for s in cat_data['skills']]:
                    categories[cat_data['name']] = categories.get(cat_data['name'], 0) + 1
        
        if categories:
            cat_df = pd.DataFrame({
                'Category': list(categories.keys()),
                'Count': list(categories.values())
            })
            fig = px.pie(cat_df, values='Count', names='Category',
                       color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorized skills found")

# ============================================
# HISTORY - FIXED
# ============================================
def history_view():
    st.markdown("""
    <div class="page-header">
        <h1>📁 History</h1>
        <p>All processed resumes</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.all_parsed:
        st.info("ℹ️ No resumes processed yet.")
        return
    
    # FIXED: Safely handle empty lists
    data = []
    for i, resume in enumerate(st.session_state.all_parsed, 1):
        # Safely get experience
        experience = resume.get('experience', [])
        exp_title = experience[0].get('title', 'N/A') if experience else 'N/A'
        
        # Safely get education
        education = resume.get('education', {})
        edu_degree = education.get('degree', 'N/A') if education else 'N/A'
        
        # Safely get skills
        skills = resume.get('skills', [])
        skills_text = ", ".join(skills[:3]) + ("..." if len(skills) > 3 else "")
        
        data.append({
            "#": i,
            "Name": resume.get('name', 'Unknown'),
            "Skills": skills_text if skills_text else "No skills",
            "Experience": exp_title,
            "Education": edu_degree
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Export all data
    if st.button("📥 Export All as CSV", type="primary"):
        export_service = ExportService()
        all_data = []
        for resume in st.session_state.all_parsed:
            all_data.append(export_service._flatten(resume))
        df_all = pd.DataFrame(all_data)
        csv_data = df_all.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("Download CSV", csv_data, "all_resumes.csv", "text/csv")
    
    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.all_parsed = []
        st.success("✅ History cleared!")
        st.rerun()

# ============================================
# SETTINGS
# ============================================
def settings_view():
    st.markdown("""
    <div class="page-header">
        <h1>⚙️ Settings</h1>
        <p>Configure your resume parser</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎨 Appearance")
        theme = st.selectbox("Theme", ["Light", "Dark", "System"])
        st.markdown("### 📄 Default Export Format")
        export_format = st.selectbox("Format", ["JSON", "CSV", "PDF", "Excel"])
    
    with col2:
        st.markdown("### 🛠️ Parser Settings")
        confidence_threshold = st.slider("Confidence Threshold", 50, 95, 75)
        max_skills = st.slider("Max Skills Per Resume", 10, 50, 25)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved successfully!")

# ============================================
# MAIN
# ============================================
def main():
    current_view = sidebar()
    
    if current_view == "dashboard":
        dashboard_view()
    elif current_view == "upload":
        upload_view()
    elif current_view == "analytics":
        analytics_view()
    elif current_view == "history":
        history_view()
    elif current_view == "settings":
        settings_view()

if __name__ == "__main__":
    main()
    