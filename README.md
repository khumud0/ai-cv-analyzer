# AI-CV-Analyzer

AI-CV-Analyzer is a lightweight FastAPI service that automatically screens PDF resumes against a job description using an LLM (Google Gemini). It extracts text from uploaded PDFs, scores candidate-job fit, identifies matching and missing skills, and returns a structured JSON analysis suitable for downstream automation or dashboards.

## Repository Layout

- `main.py` — FastAPI application entrypoint and HTTP handlers
- `requirements.txt` — Python dependencies
- `Dockerfile` — Container image definition

## Key Features

- **PDF parsing:** Extracts text from uploaded PDF resumes.
- **LLM-powered analysis:** Uses the configured Gemini model to compare resumes to job descriptions and produce a score and structured feedback.
- **Standard JSON responses:** Returns consistent fields: overall score (0-100), matching skills, missing skills, and a short summary.
- **Swagger UI:** Interactive API docs available when running the server.

## Quickstart

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Provide required environment variables (example `.env`):

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Run the API locally:

```bash
python -m uvicorn main:app --reload
```

Open the interactive docs at `http://127.0.0.1:8000/docs`.

## Usage

POST `/analyze-resume` — upload a PDF resume and include a job description in the request body. The API returns a JSON object with a compatibility score, arrays of matching and missing skills, and a short professional summary.

### Example Using curl

```bash
curl -X POST "[http://127.0.0.1:8000/analyze-resume](http://127.0.0.1:8000/analyze-resume)" \
    -F "file=@/path/to/resume.pdf" \
    -F "job_description=Senior Python developer with experience in FastAPI and Docker"
```

### Response (Example)

```json
{
    "score": 85,
    "matching_skills": ["Python", "FastAPI"],
    "missing_skills": ["Docker", "Kubernetes"],
    "summary": "Candidate is a good fit with solid backend foundations but lacks containerization experience."
}
```

## Configuration

Environment variables used by the project:

- `GEMINI_API_KEY` — required, API key for Google Gemini.

## Docker

Build and run the containerized API:

```bash
docker build -t ai-cv-analyzer .
docker run -e GEMINI_API_KEY=$GEMINI_API_KEY -p 8000:8000 ai-cv-analyzer
```

## Development

- Run the server locally with `python -m uvicorn main:app --reload`.
- Add tests and linters as needed; keep changes minimal and focused.