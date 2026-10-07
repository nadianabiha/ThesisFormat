from pathlib import Path

from .docx_parser import parse_docx
from .pdf_parser import parse_pdf


def parse_document(file_path):
    """
    Memilih parser berdasarkan ekstensi file.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".docx":
        return parse_docx(file_path)

    if extension == ".pdf":
        return parse_pdf(file_path)

    raise ValueError(
        f"Format file tidak didukung: {extension}"
    )