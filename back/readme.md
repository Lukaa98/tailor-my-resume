# Backend

FastAPI backend for resume parsing.

The full project flow is documented in:

- [README.md](C:/Users/13477/Desktop/DevProjects/tailor-my-resume/README.md:1)

## Setup

### 1. Create the virtual environment

```bash
python -m venv venv
```

### 2. Activate it

Git Bash:

```bash
source venv/Scripts/activate
```

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Edit [back/.env](C:/Users/13477/Desktop/DevProjects/tailor-my-resume/back/.env:1) and set:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### 5. Run the API

```bash
uvicorn src.main:app --reload --port 8081
```

API base URL:

- [http://127.0.0.1:8081](http://127.0.0.1:8081)

Main production endpoint:

- `POST /api/resumes/parse`

Debug endpoints:

- `POST /api/debug/resumes/layout`
- `POST /api/debug/resumes/lines`
- `POST /api/debug/resumes/sections`
