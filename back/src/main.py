from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from src.config import get_settings
from src.services.pdf_parser import extract_resume_with_layout
from src.services.layout_text_extractor import extract_readable_text
from src.services.section_parser import extract_sections
from src.services.pdf_exporter import export_resume_pdf

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(title="Resume Import / Export API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}


@app.head("/")
def health_head():
    return


def format_numbered_lines(text: str) -> str:
    return "\n".join(
        f"{index:03d}: {line}"
        for index, line in enumerate(text.splitlines())
    )


def build_resume_lines(layout_data: dict) -> dict:
    extracted = extract_readable_text(layout_data)
    logger.info(
        "Extracted resume text for analysis:\n%s",
        format_numbered_lines(extracted["text"]),
    )
    return extracted


def build_resume_sections(payload: dict) -> dict:
    if "text" not in payload:
        raise ValueError("Missing text")

    semantic = extract_sections(payload["text"])
    logger.info("Resume section analysis result: %s", semantic)
    return {
        "semantic": semantic,
        "line_map": payload.get("line_map", []),
    }

# -------------------------
# 1️⃣ Lossless layout
# -------------------------

@app.post("/api/resumes/parse")
async def parse_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "PDF only"})

    layout = extract_resume_with_layout(file.file)
    lines = build_resume_lines(layout)

    try:
        sections = build_resume_sections(lines)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        logger.exception("Resume analysis failed")
        return JSONResponse(status_code=502, content={"error": f"Resume analysis failed: {exc}"})

    return {
        "layout": layout,
        "lines": lines,
        "sections": sections["semantic"],
    }


# Debug endpoint: extract layout only.
@app.post("/api/debug/resumes/layout")
async def extract_resume_layout(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "PDF only"})

    layout = extract_resume_with_layout(file.file)
    return layout

# -------------------------
# 2️⃣ Clean text extractor
# -------------------------

# Debug endpoint: convert layout JSON into readable lines.
@app.post("/api/debug/resumes/lines")
async def extract_resume_lines(layout_data: dict):
    if "pages" not in layout_data:
        return JSONResponse(status_code=400, content={"error": "Missing layout pages"})

    return build_resume_lines(layout_data)

# -------------------------
# 3️⃣ Semantic analysis
# -------------------------

# Debug endpoint: analyze sections from extracted lines.
@app.post("/api/debug/resumes/sections")
async def analyze_resume_sections(payload: dict):
    """
    Expects:
    {
      "text": "clean resume text"
    }
    """

    try:
        return build_resume_sections(payload)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        logger.exception("Resume analysis failed")
        return JSONResponse(status_code=502, content={"error": f"Resume analysis failed: {exc}"})

# -------------------------
# 4️⃣ Export PDF
# -------------------------

@app.post("/api/resumes/export")
async def export_resume_pdf_file(layout_data: dict):
    pdf = export_resume_pdf(layout_data)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resume.pdf"}
    )
