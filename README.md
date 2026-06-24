# 🚀 AI Resume Parser

## Professional Resume Parsing & Analysis Tool

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-FF4B4B.svg)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Features

- 📄 Parse PDF, DOCX, and TXT resumes
- 🧠 Extract skills, experience, and education
- 📊 Interactive analytics dashboard
- 💾 Export to JSON, CSV, PDF, and Excel
- 🎯 Skill match scoring
- 📈 Visual insights and trends
- ⚡ Batch processing

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run the app
streamlit run app/main.py
```

## 📁 Project Structure

```
ai-resume-parser/
├── app/
│   ├── main.py      # Streamlit UI
│   ├── parser.py    # Core parser
│   ├── skills.py    # Skill extraction
│   ├── export.py    # Export services
│   └── utils.py     # Utilities
├── assets/
│   └── style.css    # Custom styling
├── data/
│   └── skills.json  # Skills database
└── requirements.txt
```

## 🐳 Docker

```bash
docker-compose up -d
# Open http://localhost:8501
```

## 📝 License

MIT
```

---

## 🎯 COMPLETE SUMMARY

| File | Purpose | Lines |
|------|---------|-------|
| `app/main.py` | Professional UI with dashboard | 400+ |
| `assets/style.css` | Custom styling & animations | 300+ |
| `app/parser.py` | Core parsing logic | 300+ |
| `app/export.py` | Export services | 150+ |
| `app/skills.py` | Skill extraction | 80+ |
| `app/utils.py` | Utilities | 70+ |
| `app/config.py` | Configuration | 50+ |
| `data/skills.json` | Skills database | 200+ |
| **TOTAL** | | **1,550+** |

## ✅ Key Improvements

1. **Professional UI** - Clean design with gradients and animations
2. **Dashboard View** - Metrics, charts, and activity feed
3. **Skill Tags** - Beautiful colored skill tags with animations
4. **Export Options** - JSON, CSV, PDF, Excel with download buttons
5. **Dark Mode Ready** - CSS supports dark theme
6. **Responsive** - Works on all devices
7. **Streamlined Structure** - Removed unnecessary folders
8. **Optimized Code** - Clean, well-organized modules

## 🚀 How to Run

```bash
# 1. Clone/Download
cd ai-resume-parser

# 2. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Run
streamlit run app/main.py

# 4. Open http://localhost:8501
