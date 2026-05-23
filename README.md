# Tailor My Resume

Full-stack resume parsing app with:

- `front/` React UI
- `back/` FastAPI parsing API

## Dev Setup

### Backend

Git Bash:

```bash
cd ~/Desktop/DevProjects/tailor-my-resume/back
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Set [back/.env](C:/Users/13477/Desktop/DevProjects/tailor-my-resume/back/.env:1):

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Run:

```bash
uvicorn src.main:app --reload --port 8081
```

Backend URL:

- [http://127.0.0.1:8081](http://127.0.0.1:8081)

Production backend:

- [https://tailor-my-resume-api.onrender.com/](https://tailor-my-resume-api.onrender.com/)

### Frontend

Git Bash:

```bash
cd ~/Desktop/DevProjects/tailor-my-resume/front
npm install
npm start
```

Frontend URL:

- [http://localhost:3000](http://localhost:3000)

## GitHub Actions

Workflows:

- `.github/workflows/pages.yml`

`pages.yml` deploys the frontend to GitHub Pages.

Before using the Pages workflow, set this repository secret:

- `REACT_APP_API_URL`

This can point to your deployed backend URL, for example:

```text
https://tailor-my-resume-api.onrender.com
```

Frontend API behavior:

- local browser on `localhost` uses `http://localhost:8081`
- deployed frontend must provide `REACT_APP_API_URL`
- `REACT_APP_API_URL` should point to the deployed backend

## Main API

Production flow uses:

- `POST /api/resumes/parse`
- `POST /api/resumes/export`

Debug-only endpoints:

- `POST /api/debug/resumes/layout`
- `POST /api/debug/resumes/lines`
- `POST /api/debug/resumes/sections`

## Parse Flow

`POST /api/resumes/parse` returns:

```json
{
  "layout": {},
  "lines": {
    "text": "",
    "line_map": []
  },
  "sections": {
    "sections": [
      {
        "type": "experience",
        "header": "Experience",
        "start_line": 0,
        "end_line": 10
      }
    ],
    "parser": "hybrid"
  }
}
```

Current parser behavior:

- extracts PDF layout with PyMuPDF
- converts layout into ordered text lines
- detects section headers with code first
- uses AI only for ambiguous header classification
- preserves the original resume header in `header`

## Current UI

The resume editor currently:

- uploads a PDF
- shows parsed sections in a sticky sidebar
- highlights matching PDF text on hover/click
- shows parser mode and line ranges

Main frontend files:

- [ResumeEditor.jsx](C:/Users/13477/Desktop/DevProjects/tailor-my-resume/front/src/components/ResumeEditor/ResumeEditor.jsx:1)
- [LosslessResumeViewer.jsx](C:/Users/13477/Desktop/DevProjects/tailor-my-resume/front/src/components/ResumeEditor/LosslessResumeViewer.jsx:1)

Main backend files:

- [main.py](C:/Users/13477/Desktop/DevProjects/tailor-my-resume/back/src/main.py:1)
- [section_parser.py](C:/Users/13477/Desktop/DevProjects/tailor-my-resume/back/src/services/section_parser.py:1)
- [pdf_parser.py](C:/Users/13477/Desktop/DevProjects/tailor-my-resume/back/src/services/pdf_parser.py:1)
- [layout_text_extractor.py](C:/Users/13477/Desktop/DevProjects/tailor-my-resume/back/src/services/layout_text_extractor.py:1)
