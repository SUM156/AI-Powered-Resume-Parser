"""FastAPI REST API for the resume parser."""
from io import BytesIO
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from pydantic import BaseModel

from src.parser import ResumeParser
from src.matcher import JobMatcher
from src.database import DatabaseService
from src.export import ExportService
from src.logger import logger
from src import config

app = FastAPI(title="AI Resume Parser API", version="1.0.0")

parser = ResumeParser()
matcher = JobMatcher()
db = DatabaseService()
exporter = ExportService()


class MatchRequest(BaseModel):
    resume_id: int
    job_description: str


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/v1/parse")
async def parse_resume(file: UploadFile = File(...)):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    content = await file.read()
    if len(content) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, "File too large")

    try:
        result = parser.parse_resume(BytesIO(content), file.filename)
    except Exception as e:
        logger.error(f"Parse failed: {e}")
        raise HTTPException(500, str(e))

    result.pop("raw_text", None)
    resume_id = db.save_resume(result)
    result["id"] = resume_id
    return result


@app.get("/api/v1/resumes")
def list_resumes(limit: int = Query(50, le=200), offset: int = 0):
    return db.get_resumes(limit=limit, offset=offset)


@app.get("/api/v1/resumes/{resume_id}")
def get_resume(resume_id: int):
    resume = db.get_resume(resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found")
    return resume


@app.delete("/api/v1/resumes/{resume_id}")
def delete_resume(resume_id: int):
    if not db.delete_resume(resume_id):
        raise HTTPException(404, "Resume not found")
    return {"deleted": True}


@app.get("/api/v1/search")
def search_resumes(q: str):
    return db.search_resumes(q)


@app.post("/api/v1/match")
def match_resume(req: MatchRequest):
    resume = db.get_resume(req.resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found")
    return matcher.match(resume, req.job_description)


@app.get("/api/v1/analytics")
def analytics():
    return db.get_analytics()
