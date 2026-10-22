from pathlib import Path

import pdfplumber


def parse_pdf(file_path):
    """
    Membaca file PDF dan mengambil informasi dasar
    yang dibutuhkan ThesisFormat.
    """

    pages = []
    total_text = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                    "width": page.width,
                    "height": page.height,
                }
            )

            total_text.append(text)

    return {
        "file_name": Path(file_path).name,
        "page_count": len(pages),
        "text": "\n".join(total_text),
        "pages": pages,
    }