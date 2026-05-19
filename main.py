import os
import io
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("CRITICAL ERROR: GEMINI_API_KEY is not set in the .env file or environment variables.")

client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(
    title="AI-Powered Resume Screener & Analyzer API",
    description="An AI-driven API to screen resumes against job descriptions using Google Gemini.",
    version="1.0.0"
)

class ResumeAnalysisResult(BaseModel):
    score: int = Field(..., description="Overall matching score between 0 and 100")
    matching_skills: list[str] = Field(..., description="Skills found in both the resume and job description")
    missing_skills: list[str] = Field(..., description="Required skills from the job description missing in the resume")
    summary: str = Field(..., description="A brief professional summary of the candidate's fit for the role")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read and parse the PDF file: {str(e)}")

@app.post("/analyze-resume")
async def analyze_resume(
    job_description: str = Form(..., description="The full text of the job vacancy"),
    file: UploadFile = File(..., description="The resume PDF file to analyze")
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")

    file_bytes = await file.read()
    resume_text = extract_text_from_pdf(file_bytes)

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="The provided PDF is empty or contains no readable text.")

    prompt = f"""
    You are an expert Senior IT Recruiter. Analyze this resume against the job description.
    You MUST respond with a JSON object that matches this structure exactly:
    {{
        "score": 85,
        "matching_skills": ["Python", "FastAPI"],
        "missing_skills": ["Docker"],
        "summary": "Candidate is a good fit."
    }}
    
    Job Description: {job_description}
    Resume Text: {resume_text}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.split("```json")[1].split("```")[0].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text.split("```")[1].split("```")[0].strip()
            
        return json.loads(clean_text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")