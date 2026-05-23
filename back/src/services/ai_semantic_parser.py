import json
from typing import Dict
import httpx
from openai import OpenAI
from src.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """
You are a resume analyzer.

You DO NOT change text.
You DO NOT rewrite content.

Your task:
- Identify resume sections from the text.
- Sections start at their header line.
- Sections end immediately BEFORE the next section header.

Rules:
- Line numbers are 0-based.
- Contact info may appear at the top OR bottom.
- If unsure, keep sections smaller rather than larger.
- Do NOT merge unrelated sections.

Return JSON ONLY in this format:
{
  "sections": [
    {
      "type": "experience",
      "start_line": 10,
      "end_line": 22
    }
  ]
}

Valid section types:
- contact_info
- education
- experience
- skills
- projects
- certificates
- training
- publications
- community
- other
"""

HEADER_CLASSIFICATION_PROMPT = """
You classify resume section header candidates.

You will receive short resume lines that may or may not be section headers.
For each line, return:
- the original line
- a section type if it is a real resume section header
- "ignore" if it is not a section header

Valid section types:
- education
- experience
- skills
- projects
- certificates
- training
- publications
- community
- other
- ignore

Rules:
- Focus on the meaning of the line, not exact wording.
- Examples that should map to experience: "Work Experience", "Professional Experience", "Career History", "Employment".
- Examples that should map to skills: "Technical Skills", "Core Competencies", "Tools & Technologies".
- Examples that should map to publications: "Publications", "Research", "Selected Publications".
- Examples that should map to community: "Open Source", "Community", "Open Source & Community", "Leadership & Community".
- If a line looks like a job title, company name, date, or content line, return "ignore".
- Return JSON ONLY in this format:
{
  "headers": [
    { "line": "Professional Background", "type": "experience" },
    { "line": "Brooklyn College final project", "type": "ignore" }
  ]
}
"""

def analyze_resume_semantics(text: str) -> Dict:
    if not settings.openai_api_key or not settings.openai_api_key.strip():
        raise ValueError("OPENAI_API_KEY is missing in back/.env")

    http_client = httpx.Client(trust_env=False)
    client = OpenAI(
        api_key=settings.openai_api_key,
        http_client=http_client
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON returned by LLM:\n{content}")

    if "sections" not in result:
        raise ValueError("Missing 'sections' in LLM response")

    return result


def classify_section_headers(lines: list[str]) -> Dict[str, str]:
    if not lines:
        return {}

    if not settings.openai_api_key or not settings.openai_api_key.strip():
        return {}

    http_client = httpx.Client(trust_env=False)
    client = OpenAI(
        api_key=settings.openai_api_key,
        http_client=http_client
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": HEADER_CLASSIFICATION_PROMPT},
            {"role": "user", "content": json.dumps({"lines": lines})}
        ],
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        return {}

    headers = result.get("headers", [])
    classified: Dict[str, str] = {}

    for item in headers:
        line = item.get("line")
        header_type = item.get("type")
        if not isinstance(line, str) or not isinstance(header_type, str):
            continue
        if header_type == "ignore":
            continue
        classified[line] = header_type

    return classified
