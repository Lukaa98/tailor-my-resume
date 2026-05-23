import re
from typing import Dict, List, Optional

from src.services.ai_semantic_parser import analyze_resume_semantics, classify_section_headers


SECTION_PATTERNS = [
    ("education", re.compile(r"^\s*(education|academic background|academics?)\s*$", re.IGNORECASE)),
    (
        "skills",
        re.compile(
            r"^\s*(relevant professional skills|technical skills|skills|core competencies|tools(?:\s*&\s*technologies)?|technologies)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        "experience",
        re.compile(
            r"^\s*(work experience|professional experience|experience|employment history|career history|professional background|work history)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        "projects",
        re.compile(
            r"^\s*projects?\b(?:\s*(?:[-|:])\s*.*|\s+(?:[A-Za-z]{3,9}\s+\d{4}|\d{4}))?\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        "training",
        re.compile(r"^\s*(training|professional training|bootcamps?|coursework)\s*$", re.IGNORECASE),
    ),
    (
        "certificates",
        re.compile(
            r"^\s*(certificates|certifications|licenses|licenses and certifications)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        "publications",
        re.compile(
            r"^\s*(publications|selected publications|research publications|research)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        "community",
        re.compile(
            r"^\s*(open source(?:\s*&\s*community)?|community|leadership\s*&\s*community)\s*$",
            re.IGNORECASE,
        ),
    ),
]


def extract_sections(text: str) -> Dict:
    heuristic_sections = detect_sections_by_headers(text)
    if heuristic_sections:
        return {
            "sections": heuristic_sections,
            "parser": "hybrid",
        }

    ai_sections = analyze_resume_semantics(text)
    ai_sections["parser"] = "ai"
    return ai_sections


def detect_sections_by_headers(text: str) -> List[Dict]:
    lines = text.splitlines()
    if not lines:
        return []

    header_hits: List[Dict] = []
    unknown_candidates: List[Dict] = []

    for index, raw_line in enumerate(lines):
        normalized = normalize_line(raw_line)
        if not normalized:
            continue

        section_type = match_section_header(normalized)
        if section_type:
            header_hits.append({"type": section_type, "line": index})
            continue

        if is_header_candidate(raw_line):
            unknown_candidates.append(
                {
                    "raw": raw_line.strip(),
                    "normalized": normalized,
                    "line": index,
                }
            )

    ai_classified = classify_section_headers([item["raw"] for item in unknown_candidates])

    for candidate in unknown_candidates:
        section_type = ai_classified.get(candidate["raw"])
        if section_type:
            header_hits.append(
                {
                    "type": section_type,
                    "line": candidate["line"],
                    "header": candidate["raw"],
                }
            )

    if not header_hits:
        return []

    header_hits.sort(key=lambda item: item["line"])
    header_hits = dedupe_adjacent_headers(header_hits)

    sections: List[Dict] = []
    first_header_line = header_hits[0]["line"]

    if first_header_line > 0:
        sections.append(
            {
                "type": "contact_info",
                "header": "Contact Info",
                "start_line": 0,
                "end_line": first_header_line - 1,
            }
        )

    for current, next_header in zip(header_hits, header_hits[1:] + [None]):
        start_line = current["line"]
        end_line = (next_header["line"] - 1) if next_header else len(lines) - 1

        sections.append(
            {
                "type": current["type"],
                "header": current.get("header", lines[start_line].strip()),
                "start_line": start_line,
                "end_line": end_line,
            }
        )

    return sections


def match_section_header(line: str) -> Optional[str]:
    for section_type, pattern in SECTION_PATTERNS:
        if pattern.match(line):
            return section_type
    return None


def is_header_candidate(line: str) -> bool:
    normalized = normalize_line(line)
    if not normalized:
        return False

    if "@" in normalized:
        return False

    if normalized.startswith(("•", "●", "-", "*")):
        return False

    if len(normalized) > 50:
        return False

    word_count = len(normalized.split())
    if word_count > 6:
        return False

    if has_sentence_punctuation(normalized):
        return False

    if contains_date_range(normalized):
        return False

    uppercase_ratio = get_uppercase_ratio(normalized)
    looks_all_caps = uppercase_ratio >= 0.7
    looks_title_case = normalized == normalized.title()

    return looks_all_caps or looks_title_case


def dedupe_adjacent_headers(header_hits: List[Dict]) -> List[Dict]:
    deduped: List[Dict] = []

    for hit in header_hits:
        if deduped and deduped[-1]["line"] == hit["line"]:
            continue
        deduped.append(hit)

    return deduped


def has_sentence_punctuation(line: str) -> bool:
    return any(mark in line for mark in [".", ";", ":"])


def contains_date_range(line: str) -> bool:
    return bool(
        re.search(
            r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|\d{4})\b",
            line,
            re.IGNORECASE,
        )
    )


def get_uppercase_ratio(line: str) -> float:
    letters = [char for char in line if char.isalpha()]
    if not letters:
        return 0.0

    uppercase = sum(1 for char in letters if char.isupper())
    return uppercase / len(letters)


def normalize_line(line: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        line.replace("•", "").replace("●", "").replace("â€¢", "").replace("â—", ""),
    ).strip()
