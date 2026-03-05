import re
from dataclasses import dataclass
from typing import Dict, List

MIN_CHAR_COUNT = 100
MIN_TOKEN_COUNT = 25
MIN_RESUME_CONFIDENCE = 40

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4})\b")
LINK_PATTERN = re.compile(r"\b(?:linkedin\.com|github\.com|portfolio|behance\.net)\b")

SECTION_KEYWORDS: Dict[str, List[str]] = {
    "skills": ["skills", "technical skills", "technicalskills", "core competencies", "tech stack", "skills&other"],
    "education": ["education", "academic qualification", "academics"],
    "experience_projects": [
        "experience",
        "work experience",
        "workexperience",
        "professional experience",
        "professionalexperience",
        "employment",
        "projects",
        "project",
        "internship",
    ],
    "certifications_achievements": ["certifications", "certification", "achievements", "awards", "accomplishments"],
    "summary_profile": ["summary", "profile", "objective", "about me"],
}

TECHNICAL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "angular",
    "vue",
    "node",
    "fastapi",
    "django",
    "flask",
    "spring",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "git",
    "linux",
    "machine learning",
    "data science",
}

NON_RESUME_INDICATORS = {
    "unit-i",
    "unit ii",
    "chapter",
    "syllabus",
    "assignment",
    "question bank",
    "introduction to",
    "course outcomes",
    "learning outcomes",
    "theory",
    "module",
    "lecture",
    "experiment",
    "lab manual",
}


@dataclass
class ResumeValidationResult:
    is_valid: bool
    confidence_score: int
    detected_sections: List[str]
    missing_sections: List[str]
    message: str


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _normalize_line_for_heading(line: str) -> str:
    normalized = line.strip().lower()
    normalized = re.sub(r"^[\-\u2022\*\.\d\)\(]+\s*", "", normalized)
    normalized = re.sub(r"[:\-]+$", "", normalized).strip()
    return normalized


def _canonical_form(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _extract_lines(text: str) -> List[str]:
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def _is_heading_candidate(line: str) -> bool:
    cleaned = _normalize_line_for_heading(line)
    word_count = len(cleaned.split())
    if word_count == 0 or word_count > 6:
        return False
    if cleaned.endswith("."):
        return False
    return True


def _contains_contact_info(lines: List[str], normalized_text: str) -> bool:
    if EMAIL_PATTERN.search(normalized_text):
        return True

    if LINK_PATTERN.search(normalized_text):
        return True

    for line in lines:
        lower_line = line.lower()
        if PHONE_PATTERN.search(line) and any(token in lower_line for token in {"phone", "mobile", "contact", "+"}):
            return True
    return False


def _section_present(lines: List[str], keywords: List[str]) -> bool:
    keyword_set = {keyword.lower() for keyword in keywords}
    canonical_keywords = {_canonical_form(keyword) for keyword in keywords}
    for line in lines:
        if not _is_heading_candidate(line):
            continue
        cleaned = _normalize_line_for_heading(line)
        canonical_cleaned = _canonical_form(cleaned)
        if cleaned in keyword_set:
            return True
        if canonical_cleaned in canonical_keywords:
            return True
        # Handle inline headings like "skills: python, sql" or compact headings like "workexperience".
        if any(cleaned.startswith(f"{keyword}:") or cleaned.startswith(f"{keyword} -") for keyword in keyword_set):
            return True
        if any(canonical_cleaned.startswith(keyword) for keyword in canonical_keywords):
            return True
    return False


def validate_resume_document(text: str) -> ResumeValidationResult:
    normalized_text = _normalize_text(text)
    lines = _extract_lines(text)
    token_count = len(normalized_text.split())

    if not normalized_text or len(normalized_text) < MIN_CHAR_COUNT or token_count < MIN_TOKEN_COUNT:
        return ResumeValidationResult(
            is_valid=False,
            confidence_score=0,
            detected_sections=[],
            missing_sections=["readable_content"],
            message=(
                "Unable to analyze the document. The file does not contain enough readable content to be identified "
                "as a resume. Please upload a valid resume in PDF or DOCX format."
            ),
        )

    score = 0
    detected_sections: List[str] = []

    if _contains_contact_info(lines, normalized_text):
        score += 25
        detected_sections.append("contact_information")

    if _section_present(lines, SECTION_KEYWORDS["skills"]):
        score += 20
        detected_sections.append("skills")

    if _section_present(lines, SECTION_KEYWORDS["education"]):
        score += 15
        detected_sections.append("education")

    if _section_present(lines, SECTION_KEYWORDS["experience_projects"]):
        score += 20
        detected_sections.append("experience_or_projects")

    if _section_present(lines, SECTION_KEYWORDS["certifications_achievements"]):
        score += 10
        detected_sections.append("certifications_or_achievements")

    if _section_present(lines, SECTION_KEYWORDS["summary_profile"]):
        score += 5
        detected_sections.append("summary_or_profile")

    technical_hits = sum(1 for keyword in TECHNICAL_KEYWORDS if keyword in normalized_text)
    if technical_hits >= 5:
        score += 10
        detected_sections.append("technical_keywords")

    non_resume_hits = sum(1 for marker in NON_RESUME_INDICATORS if marker in normalized_text)
    section_heading_count = len(
        {"skills", "education", "experience_or_projects", "certifications_or_achievements", "summary_or_profile"}
        .intersection(set(detected_sections))
    )

    required = {
        "contact_information",
        "skills",
        "education",
        "experience_or_projects",
    }
    missing_sections = sorted(required - set(detected_sections))

    # Hard gates for worst-case handling:
    # 1) contact info must exist
    # 2) at least two resume section headings must be present
    # 3) strongly non-resume documents are rejected
    has_contact = "contact_information" in detected_sections
    has_enough_headings = section_heading_count >= 2
    non_resume_document = non_resume_hits >= 3 and section_heading_count <= 2

    is_valid = (
        score >= MIN_RESUME_CONFIDENCE
        and has_contact
        and has_enough_headings
        and not non_resume_document
    )

    score = min(score, 100)

    if not is_valid:
        message = (
            "This document does not appear to be a valid resume. Please upload a recent professional resume that "
            "includes sections such as Skills, Education, Work Experience or Projects, and Contact Information. "
            "Supported formats: PDF or DOCX."
        )
    else:
        message = "Resume validation passed."

    return ResumeValidationResult(
        is_valid=is_valid,
        confidence_score=score,
        detected_sections=sorted(detected_sections),
        missing_sections=missing_sections,
        message=message,
    )
