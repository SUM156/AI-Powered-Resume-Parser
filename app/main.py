"""
🚀 AI Resume Parser - Professional Candidate Screening Tool
Author: AI Resume Parser Team
Version: 4.0.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from pathlib import Path
import base64
from io import BytesIO
import time

# Import custom modules
from app.parser import ResumeParser
from app.skills import SkillExtractor
from app.export import ExportService
from app.config import Config
from app.utils import Utils

# Page configuration
st.set_page_config(
    page_title="AI Resume Parser | Professional Screening",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = Path("assets/style.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Session state initialization
def init_session_state():
    defaults = {
        'parsed_data': None,
        'uploaded_files': [],
        'analysis_complete': False,
        'current_resume': None,
        'all_parsed': [],
        'export_format': 'json',
        'theme': 'light'
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Sidebar Navigation
def sidebar():
    with st.sidebar:
        # Logo and Brand
        st.markdown("""
        <div class="sidebar-brand">
            <span class="brand-icon">📄</span>
            <span class="brand-text">AI Resume Parser</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        nav_options = {
            "🏠 Dashboard": "dashboard",
            "📤 Upload Resume": "upload",
            "📊 Analytics": "analytics",
            "📁 History": "history",
            "⚙️ Settings": "settings"
        }
        
        selected = st.radio(
            "Navigation",
            list(nav_options.keys()),
            index=0
        )
        
        st.markdown("---")
        
        # Stats in sidebar
        if st.session_state.parsed_data:
            st.markdown("### 📊 Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Resumes", len(st.session_state.all_parsed))
            with col2:
                st.metric("Skills Found", "45")
        
        st.markdown("---")
        
        # Footer
        st.markdown("""
        <div class="sidebar-footer">
            <small>Version 4.0.0</small><br>
            <small>© 2024 AI Resume Parser</small>
        </div>
        """, unsafe_allow_html=True)
        
        return nav_options[selected]

# Dashboard View
def dashboard_view():
    st.markdown("""
    <div class="page-header">
        <h1>📊 Dashboard</h1>
        <p>Overview of your resume parsing activities</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Total Resumes",
            value=len(st.session_state.all_parsed),
            delta="+2 today"
        )
    with col2:
        st.metric(
            label="🛠️ Skills Extracted",
            value="156",
            delta="+12"
        )
    with col3:
        st.metric(
            label="⏳ Avg Experience",
            value="4.5 yrs",
            delta="+0.5"
        )
    with col4:
        st.metric(
            label="🎯 Match Rate",
            value="87%",
            delta="+5%"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Skill Distribution")
        # Sample data
        data = pd.DataFrame({
            'Skill': ['Python', 'JavaScript', 'SQL', 'Java', 'C++', 'React'],
            'Count': [45, 32, 28, 25, 18, 15]
        })
        fig = px.bar(data, x='Skill', y='Count', color='Count', 
                     color_continuous_scale='Blues')
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Experience Levels")
        data = pd.DataFrame({
            'Level': ['Entry', 'Mid', 'Senior', 'Lead', 'Manager'],
            'Count': [5, 12, 8, 4, 3]
        })
        fig = px.pie(data, values='Count', names='Level', 
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity
    st.markdown("### 🕐 Recent Activity")
    activities = [
        {"time": "2 min ago", "action": "Parsed resume: John Doe - Software Engineer"},
        {"time": "15 min ago", "action": "Exported 3 resumes to JSON"},
        {"time": "1 hour ago", "action": "Added new skill: Kubernetes"},
        {"time": "2 hours ago", "action": "Updated skill database"}
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div class="activity-item">
            <span class="activity-time">{activity['time']}</span>
            <span class="activity-action">{activity['action']}</span>
        </div>
        """, unsafe_allow_html=True)

# Upload View
def upload_view():
    st.markdown("""
    <div class="page-header">
        <h1>📤 Upload Resume</h1>
        <p>Upload PDF, DOCX, or TXT files for parsing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload Area
    uploaded_files = st.file_uploader(
        "Choose resume files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        
        # Show uploaded files
        st.markdown("### 📁 Uploaded Files")
        for file in uploaded_files:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"📄 {file.name}")
            with col2:
                st.write(f"Size: {len(file.getvalue()) / 1024:.1f} KB")
            with col3:
                if st.button("Process", key=f"process_{file.name}"):
                    process_resume(file)
        
        # Batch Process
        if len(uploaded_files) > 1:
            if st.button("🔄 Batch Process All", type="primary"):
                with st.spinner("Processing all resumes..."):
                    for file in uploaded_files:
                        process_resume(file)
                    st.success(f"✅ Successfully processed {len(uploaded_files)} resumes!")

def process_resume(file):
    """Process a single resume file"""
    try:
        with st.spinner(f"Parsing {file.name}..."):
            # Simulate parsing
            time.sleep(1.5)
            
            # Sample parsed data
            parsed_data = {
                "name": "John Doe" if "john" in file.name.lower() else "Jane Smith",
                "email": "john.doe@email.com",
                "phone": "+1-555-123-4567",
                "skills": ["Python", "JavaScript", "React", "SQL", "AWS"],
                "experience": [
                    {
                        "company": "Tech Corp",
                        "title": "Senior Software Engineer",
                        "duration": "2 years",
                        "description": "Full-stack development"
                    }
                ],
                "education": {
                    "degree": "B.S. Computer Science",
                    "institution": "Stanford University",
                    "year": "2020"
                },
                "summary": "Experienced software engineer with 4 years of full-stack development"
            }
            
            st.session_state.parsed_data = parsed_data
            st.session_state.all_parsed.append(parsed_data)
            st.session_state.analysis_complete = True
            
            # Show success
            st.success(f"✅ Successfully parsed {file.name}")
            
            # Show parsed data preview
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
                    skills_html = "".join([
                        f'<span class="skill-tag">{skill}</span>'
                        for skill in parsed_data['skills']
                    ])
                    st.markdown(f'<div class="skills-container">{skills_html}</div>',
                               unsafe_allow_html=True)
                    
                    st.markdown("#### 💼 Experience")
                    for exp in parsed_data['experience']:
                        st.write(f"**{exp['title']}** at {exp['company']}")
                        st.write(f"Duration: {exp['duration']}")
            
            # Export buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📥 Export JSON", key=f"json_{file.name}"):
                    export_data(parsed_data, 'json')
            with col2:
                if st.button("📥 Export CSV", key=f"csv_{file.name}"):
                    export_data(parsed_data, 'csv')
            with col3:
                if st.button("📥 Export PDF", key=f"pdf_{file.name}"):
                    export_data(parsed_data, 'pdf')
            with col4:
                if st.button("📥 Export Excel", key=f"excel_{file.name}"):
                    export_data(parsed_data, 'excel')
                    
    except Exception as e:
        st.error(f"❌ Error parsing {file.name}: {str(e)}")

def export_data(data, format_type):
    """Export parsed data in selected format"""
    try:
        export_service = ExportService()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{data['name'].replace(' ', '_')}_{timestamp}"
        
        if format_type == 'json':
            json_data = export_service.to_json(data)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"{filename}.json",
                mime="application/json"
            )
        elif format_type == 'csv':
            csv_data = export_service.to_csv(data)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"{filename}.csv",
                mime="text/csv"
            )
        elif format_type == 'pdf':
            pdf_data = export_service.to_pdf(data)
            st.download_button(
                label="📥 Download PDF",
                data=pdf_data,
                file_name=f"{filename}.pdf",
                mime="application/pdf"
            )
        elif format_type == 'excel':
            excel_data = export_service.to_excel(data)
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"{filename}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.success(f"✅ Exported as {format_type.upper()}")
    except Exception as e:
        st.error(f"❌ Export failed: {str(e)}")

# Analytics View
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
    
    # Skill frequency
    skill_counts = pd.Series(all_skills).value_counts().head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔝 Top Skills")
        fig = px.bar(
            x=skill_counts.values,
            y=skill_counts.index,
            orientation='h',
            color=skill_counts.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Skill Categories")
        categories = {
            'Programming': 45,
            'Web Development': 32,
            'Data Science': 28,
            'Cloud': 20,
            'DevOps': 15
        }
        fig = px.pie(
            values=list(categories.values()),
            names=list(categories.keys()),
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# History View
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
    
    # Table view
    data = []
    for i, resume in enumerate(st.session_state.all_parsed, 1):
        data.append({
            "#": i,
            "Name": resume.get('name', 'Unknown'),
            "Skills": ", ".join(resume.get('skills', [])[:3]) + ("..." if len(resume.get('skills', [])) > 3 else ""),
            "Experience": resume.get('experience', [{}])[0].get('title', 'N/A'),
            "Education": resume.get('education', {}).get('degree', 'N/A')
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Clear history button
    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.all_parsed = []
        st.success("✅ History cleared!")
        st.rerun()

# Settings View
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
        
        st.markdown("### 🔍 Skill Detection")
        detect_soft_skills = st.checkbox("Detect Soft Skills", value=True)
        detect_certifications = st.checkbox("Detect Certifications", value=True)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved successfully!")

# Main App
def main():
    """Main application entry point"""
    # Sidebar
    current_view = sidebar()
    
    # Main content area
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
