# AI Resume Analyzer

A production-style full-stack application that analyzes resumes using NLP and role-based intelligence.  
It validates uploaded documents, extracts skills, compares them against weighted role skill graphs, and returns actionable career insights.

## Features

- Resume upload support for `PDF` and `DOCX`
- Resume text extraction pipeline (`pdfminer.six`, `python-docx`)
- Resume validation layer (rejects non-resume/low-content documents)
- NLP preprocessing (cleaning, tokenization, stopword removal, lemmatization)
- Skill extraction with synonym normalization
- Two analysis modes:
  - `Validate Resume for a Role`
  - `Find Best Roles for My Resume`
- Weighted role scoring with skill groups and alternatives
- Missing-skill recommendations, learning paths, and course suggestions
- Modern React frontend with animated multi-step UX and chart dashboard

## Tech Stack

- Backend: FastAPI, SQLAlchemy, MySQL, NLTK
- Frontend: React (Vite), Tailwind CSS, Framer Motion, Recharts
- Document Processing: pdfminer.six, python-docx

## Project Structure

```text
AI-Resume-Analyzer/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── database/
│   │   └── db_connection.py
│   ├── models/
│   │   └── database_models.py
│   ├── services/
│   │   ├── nlp_processor.py
│   │   ├── recommendation_engine.py
│   │   ├── resume_parser.py
│   │   ├── resume_validator.py
│   │   ├── role_graph_service.py
│   │   ├── scoring_engine.py
│   │   └── skill_extractor.py
│   └── main.py
├── data/
│   └── role_skill_graphs.json
├── frontend/
│   ├── src/
│   └── package.json
├── uploads/
├── requirements.txt
└── seed_data.py
```

## How It Works

### Pipeline

1. User uploads resume (`PDF`/`DOCX`)
2. Text is extracted
3. Resume validation runs
4. If valid:
   - NLP preprocessing
   - Skill extraction
   - Weighted role scoring
   - Suggestions and course recommendations
5. If invalid:
   - Analysis stops
   - User gets clear validation error

### Analysis Modes

- `validate_role`: User selects a role, system scores resume against that role
- `discover_roles`: System compares resume against all supported roles and returns ranking

## Resume Validation Logic

Validation includes:

- minimum content checks (empty/very short/low-token docs rejected)
- contact presence checks
- heading-based resume section detection
- non-resume signal rejection (assignment/syllabus/chapter-style docs)

If validation fails, analysis is blocked before scoring.

## API Endpoints

Base URL: `http://127.0.0.1:8000`

- `GET /`  
  Health message

- `GET /roles` or `GET /api/roles`  
  Returns supported role names

- `POST /analyze-resume`  
  Main public endpoint  
  Form fields:
  - `file` (required)
  - `analysis_mode` (`validate_role` or `discover_roles`)
  - `role_name` (required when `analysis_mode=validate_role`)

- `POST /api/resumes/upload`  
  Upload-only endpoint

- `POST /api/resumes/analyze`  
  Role validation analysis endpoint

## Setup

### 1. Clone repository

```bash
git clone <your-repo-url>
cd AI-Resume-Analyzer
```

### 2. Backend setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure MySQL in `app/database/db_connection.py`.

### 3. Seed role/skill tables (optional for DB-side data)

```bash
python seed_data.py
```

### 4. Run backend

```bash
uvicorn app.main:app --reload
```

Backend docs:

- Swagger UI: `http://127.0.0.1:8000/docs`

### 5. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

- `http://localhost:5173` (or next available Vite port)

Optional frontend env file:

```bash
# frontend/.env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Data Storage and Privacy (Current Behavior)

- Uploaded files are saved in local `uploads/`
- Analysis results are computed in real-time and returned in response
- Per-request analysis history is not persisted in MySQL by default
- Role intelligence currently comes from `data/role_skill_graphs.json`

If needed, add:

- automatic upload cleanup
- analysis audit/history tables
- user-level data retention policy

## Supported Roles

- Fresher
- Intern
- Junior Software Engineer
- Software Engineer
- Backend Developer
- Frontend Developer
- Full Stack Developer
- Data Analyst
- Data Scientist
- Machine Learning Engineer
- AI Engineer
- Cyber Security Analyst
- SOC Analyst
- Cloud Engineer
- DevOps Engineer
- Android Developer
- iOS Developer
- System Administrator
- Network Engineer
- Tech Lead
- Senior Software Engineer

## Known Limitations

- OCR fallback for image-only PDFs is not enabled by default
- Rule-based scoring and validation are strong but still heuristic
- Uploaded files are not auto-deleted unless cleanup is implemented

## Roadmap

- Add OCR fallback (`pytesseract`) for scanned resumes
- Persist analysis logs to database
- Add auth and per-user workspace
- Add benchmark dataset for validation/scoring accuracy
- Containerized deployment (`Docker`, `docker-compose`)

## License

Choose your preferred license (`MIT`, `Apache-2.0`, etc.) and add a `LICENSE` file.
