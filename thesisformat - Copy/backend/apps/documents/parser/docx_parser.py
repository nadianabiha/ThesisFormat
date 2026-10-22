from pathlib import Path

from docx import Document


def parse_docx(file_path):
    """
    Membaca file DOCX dan mengambil informasi
    formatting yang dibutuhkan ThesisFormat.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        runs = []

        for run in paragraph.runs:
            runs.append(
                {
                    "text": run.text,
                    "font_name": run.font.name,
                    "font_size": (
                        run.font.size.pt
                        if run.font.size
                        else None
                    ),
                    "bold": run.bold,
                    "italic": run.italic,
                    "underline": run.underline,
                }
            )

        format_info = paragraph.paragraph_format

        paragraphs.append(
            {
                "text": paragraph.text,
                "style": (
                    paragraph.style.name
                    if paragraph.style
                    else None
                ),
                "alignment": (
                    paragraph.alignment.name
                    if paragraph.alignment
                    else None
                ),
                "line_spacing": format_info.line_spacing,
                "space_before": (
                    format_info.space_before.pt
                    if format_info.space_before
                    else None
                ),
                "space_after": (
                    format_info.space_after.pt
                    if format_info.space_after
                    else None
                ),
                "first_line_indent": (
                    format_info.first_line_indent.pt
                    if format_info.first_line_indent
                    else None
                ),
                "runs": runs,
            }
        )

    sections = []

    for section in document.sections:
        sections.append(
            {
                "top_margin": section.top_margin.cm,
                "bottom_margin": section.bottom_margin.cm,
                "left_margin": section.left_margin.cm,
                "right_margin": section.right_margin.cm,
            }
        )

    return {
        "file_name": Path(file_path).name,
        "paragraphs": paragraphs,
        "sections": sections,
        "paragraph_count": len(paragraphs),
    }


def extract_docx_metadata(file_path):
    """
    Mengambil metadata umum dan informasi format dari dokumen DOCX.
    Fungsi ini menggunakan hasil parse_docx agar tidak menduplikasi
    logika ekstraksi yang sudah tersedia.
    """
    parsed = parse_docx(file_path)

    font_names = set()
    font_sizes = set()

    for paragraph in parsed["paragraphs"]:
        for run in paragraph["runs"]:
            if run["font_name"]:
                font_names.add(run["font_name"])

            if run["font_size"] is not None:
                font_sizes.add(run["font_size"])

    return {
        "file_name": parsed["file_name"],
        "paragraph_count": parsed["paragraph_count"],
        "section_count": len(parsed["sections"]),
        "sections": parsed["sections"],
        "font_names": sorted(font_names),
        "font_sizes": sorted(font_sizes),
    }