# LegalEase — AI-Powered Legal Document Generator

LegalEase is a Streamlit + FastAPI application that uses Google Gemini to generate editable legal documents and export them as TXT, DOCX, and PDF.

## Structure

```text
LegalEase/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── routes.py
├── ai_core/
│   ├── __init__.py
│   └── gemini_generator.py
├── document_utils/
│   ├── __init__.py
│   ├── sanitizer.py
│   ├── docx_formatter.py
│   ├── pdf_formatter.py
│   └── html_formatter.py
├── frontend/
│   └── app.py
├── assets/
│   └── README.txt
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── Procfile
└── README.md
```

## Windows / VS Code setup

### 1. Create the environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Gemini

Copy `.env.example` to `.env` and set:

```env
GEMINI_API_KEY=your_real_gemini_api_key
GEMINI_MODEL=gemini-1.5-pro
BACKEND_URL=http://127.0.0.1:8000
REQUEST_TIMEOUT=120
```

Never commit `.env`.

### 4. Start FastAPI

Terminal 1:

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Expected root response:

```json
{"status":"ok","service":"LegalEase API","message":"Backend is running"}
```

### 5. Start Streamlit

Terminal 2:

```powershell
streamlit run frontend/app.py
```

Open:

```text
http://localhost:8501
```

### Localhost troubleshooting

If `http://127.0.0.1:8000` says "site can't be reached", the backend is not running or has stopped because of an error.

Use exactly:

```text
http://127.0.0.1:8000
```

Do not use:

```text
http:\127.0.01.8000
```

The FastAPI terminal must remain open while you use the frontend.

## Example inputs

Document type:
`Freelance Work Contract`

Parties:
`Jane Doe (Service Provider), TechNova Inc. (Client)`

Terms:
`Payment within 30 days; Provider delivers work by agreed deadline; Confidentiality must be maintained; Either party may terminate with 15 days notice`

Effective date:
`April 15, 2026`

## API

POST `/generate`

```json
{
  "document_type": "Non-Disclosure Agreement",
  "parties": "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
  "terms": "Confidential information must be protected; Disclosure is limited to authorized personnel; Agreement lasts two years",
  "dates": "April 15, 2026"
}
```

## Legal notice

LegalEase generates draft legal text. It is not a substitute for advice from a qualified lawyer. Review generated documents for the applicable jurisdiction and circumstances before signing or relying on them.
