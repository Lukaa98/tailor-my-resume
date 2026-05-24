import re
from typing import Dict, List, Optional


MONTH_PATTERN = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
DATE_PATTERN = re.compile(
    rf"\b(?:{MONTH_PATTERN}\s+\d{{4}}|\d{{2}}/\d{{4}}|\d{{4}})\b",
    re.IGNORECASE,
)

BULLET_PREFIXES = (
    "\u2022",  # bullet
    "\u25cf",  # black circle
    "-",
    "*",
    "\u2192",  # right arrow
    "\u00a2",
    "\u00e1",
    "\u00b2",
    "\u00f5",
    "\u00db",
    "@",
    "?",
    "\u00a7",
    "\u00ae",
    "\x11",
)


def extract_section_entries(text: str, sections: List[Dict]) -> List[Dict]:
    lines = text.splitlines()
    enriched_sections: List[Dict] = []

    for section in sections:
        section_copy = dict(section)
        content_start_line = section["start_line"] + 1
        section_lines = lines[content_start_line : section["end_line"] + 1]

        if section["type"] in {"experience", "community"}:
            section_copy["entries"] = parse_experience_entries(
                section_lines,
                base_line=content_start_line,
            )

        enriched_sections.append(section_copy)

    return enriched_sections


def parse_experience_entries(lines: List[str], base_line: int = 0) -> List[Dict]:
    entries: List[Dict] = []
    current_entry: Optional[Dict] = None
    pending_header_lines: List[Dict] = []

    for offset, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue

        absolute_line = base_line + offset

        if pending_header_lines:
            if is_job_header(line):
                if current_entry and has_meaningful_content(current_entry):
                    current_entry["end_line"] = pending_header_lines[0]["line"] - 1
                    entries.append(finalize_entry(current_entry))

                header_text = " ".join(item["text"] for item in pending_header_lines + [{"text": line}])
                current_entry = {
                    "header": header_text,
                    "title": "",
                    "bullets": [],
                    "details": [],
                    "start_line": pending_header_lines[0]["line"],
                    "end_line": absolute_line,
                }
                pending_header_lines = []
                continue

            if is_title_line(line):
                if current_entry and has_meaningful_content(current_entry):
                    current_entry["end_line"] = pending_header_lines[0]["line"] - 1
                    entries.append(finalize_entry(current_entry))

                current_entry = {
                    "header": " ".join(item["text"] for item in pending_header_lines),
                    "title": clean_bullet_prefix(line),
                    "bullets": [],
                    "details": [],
                    "start_line": pending_header_lines[0]["line"],
                    "end_line": absolute_line,
                }
                pending_header_lines = []
                continue

            if looks_like_entry_preheader(line):
                pending_header_lines.append({"text": line, "line": absolute_line})
                continue

            if current_entry is not None:
                current_entry["details"].extend(item["text"] for item in pending_header_lines)
                current_entry["end_line"] = pending_header_lines[-1]["line"]
            pending_header_lines = []

        if is_job_header(line):
            if current_entry and has_meaningful_content(current_entry):
                entries.append(finalize_entry(current_entry))

            current_entry = {
                "header": line,
                "title": "",
                "bullets": [],
                "details": [],
                "start_line": absolute_line,
                "end_line": absolute_line,
            }
            continue

        if current_entry is None:
            continue

        if current_entry["bullets"] and looks_like_entry_preheader(line):
            pending_header_lines = [{"text": line, "line": absolute_line}]
            continue

        current_entry["end_line"] = base_line + offset

        if not current_entry["title"] and is_title_line(line):
            current_entry["title"] = clean_bullet_prefix(line)
            continue

        if is_bullet_line(line):
            current_entry["bullets"].append(clean_bullet_prefix(line))
        else:
            current_entry["details"].append(clean_bullet_prefix(line))

    if current_entry and has_meaningful_content(current_entry):
        entries.append(finalize_entry(current_entry))

    return entries


def is_job_header(line: str) -> bool:
    if is_bullet_line(line):
        return False

    if not DATE_PATTERN.search(line):
        return False

    if len(line) > 140:
        return False

    return True


def is_title_line(line: str) -> bool:
    if is_bullet_line(line):
        return False

    if DATE_PATTERN.search(line):
        return False

    if len(line) > 100:
        return False

    return True


def looks_like_entry_preheader(line: str) -> bool:
    if is_bullet_line(line):
        return False

    if DATE_PATTERN.search(line):
        return False

    if len(line) > 90:
        return False

    word_count = len(line.split())
    if word_count > 8:
        return False

    uppercase_ratio = get_uppercase_ratio(line)
    looks_upper = uppercase_ratio >= 0.6
    looks_title = line == line.title()

    return looks_upper or looks_title


def is_bullet_line(line: str) -> bool:
    return line.strip().startswith(BULLET_PREFIXES)


def clean_bullet_prefix(line: str) -> str:
    cleaned = line.lstrip("".join(BULLET_PREFIXES) + " ")
    return cleaned.strip()


def has_meaningful_content(entry: Dict) -> bool:
    return bool(
        entry.get("header")
        or entry.get("title")
        or entry.get("bullets")
        or entry.get("details")
    )


def finalize_entry(entry: Dict) -> Dict:
    return {
        "header": entry["header"],
        "title": entry["title"],
        "bullets": entry["bullets"],
        "details": entry["details"],
        "start_line": entry["start_line"],
        "end_line": entry["end_line"],
    }


def get_uppercase_ratio(line: str) -> float:
    letters = [char for char in line if char.isalpha()]
    if not letters:
        return 0.0

    uppercase = sum(1 for char in letters if char.isupper())
    return uppercase / len(letters)
