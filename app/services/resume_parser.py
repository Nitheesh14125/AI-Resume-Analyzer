from pathlib import Path
from uuid import uuid4

from docx import Document
from fastapi import UploadFile
from pdfminer.high_level import extract_text as extract_pdf_text

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
UPLOAD_DIR = Path("uploads")


def _get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def save_upload_file(upload_file: UploadFile) -> Path:
    extension = _get_extension(upload_file.filename or "")
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF and DOCX files are supported.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / stored_name

    with file_path.open("wb") as output_file:
        output_file.write(upload_file.file.read())

    return file_path


def extract_resume_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()
    if extension == ".pdf":
        return extract_pdf_text(str(file_path)).strip()
    if extension == ".docx":
        document = Document(file_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

    raise ValueError("Unsupported file type for extraction.")
