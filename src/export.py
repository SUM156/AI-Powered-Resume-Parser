"""
💾 Export Service Module
"""

import json
import csv
import io
from typing import Dict, List, Any
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class ExportService:
    """Export parsed data in various formats"""
    
    def to_json(self, data: Dict) -> str:
        """Export to JSON format"""
        return json.dumps(data, indent=2, default=str)
    
    def to_csv(self, data: Dict) -> str:
        """Export to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Flatten data
        flat_data = self._flatten_dict(data)
        writer.writerow(flat_data.keys())
        writer.writerow(flat_data.values())
        
        return output.getvalue()
    
    def to_pdf(self, data: Dict) -> bytes:
        """Export to PDF format"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2')
        )
        
        # Build document
        story = []
        
        # Title
        story.append(Paragraph("Resume Parsing Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Personal Info
        story.append(Paragraph("Personal Information", heading_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"Name: {data.get('name', 'Unknown')}", styles['Normal']))
        story.append(Paragraph(f"Email: {data.get('email', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Phone: {data.get('phone', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Skills
        story.append(Paragraph("Skills", heading_style))
        story.append(Spacer(1, 0.1*inch))
        skills = data.get('skills', [])
        if skills:
            skills_text = ", ".join(skills)
            story.append(Paragraph(skills_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Experience
        story.append(Paragraph("Experience", heading_style))
        story.append(Spacer(1, 0.1*inch))
        experiences = data.get('experience', [])
        for exp in experiences:
            story.append(Paragraph(f"<b>{exp.get('title', 'Unknown')}</b>", styles['Normal']))
            story.append(Paragraph(f"Company: {exp.get('company', 'Unknown')}", styles['Normal']))
            story.append(Paragraph(f"Duration: {exp.get('duration', 'Unknown')}", styles['Normal']))
            if exp.get('description'):
                story.append(Paragraph(exp['description'], styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Education
        story.append(Paragraph("Education", heading_style))
        story.append(Spacer(1, 0.1*inch))
        edu = data.get('education', {})
        story.append(Paragraph(f"Degree: {edu.get('degree', 'Unknown')}", styles['Normal']))
        story.append(Paragraph(f"Institution: {edu.get('institution', 'Unknown')}", styles['Normal']))
        story.append(Paragraph(f"Year: {edu.get('year', 'Unknown')}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return buffer.getvalue()
    
    def to_excel(self, data: Dict) -> bytes:
        """Export to Excel format"""
        # Flatten data
        flat_data = self._flatten_dict(data)
        df = pd.DataFrame([flat_data])
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Resume Data', index=False)
            
            # Auto-adjust columns
            for column in df.columns:
                column_length = max(df[column].astype(str).map(len).max(), len(str(column)))
                column_length = min(column_length, 50)
                col_idx = df.columns.get_loc(column)
                writer.sheets['Resume Data'].column_dimensions[chr(65 + col_idx)].width = column_length + 2
        
        return buffer.getvalue()
    
    def _flatten_dict(self, data: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary for CSV/Excel export"""
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    # Handle list of dicts
                    for i, item in enumerate(v):
                        items.extend(self._flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
                else:
                    items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        
        return dict(items)