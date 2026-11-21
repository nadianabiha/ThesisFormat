import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

EMU_PER_CM = 360000

# Format nomor halaman Word (w:pgNumType w:fmt) -> nama baku.
_PAGE_FORMATS = {
    "lowerRoman": "roman_lower",
    "upperRoman": "roman_upper",
    "decimal": "arabic",
}

# Perataan paragraf nomor halaman (w:jc) -> posisi horizontal.
_JC_POSITIONS = {
    "right": "right", "end": "right",
    "center": "center",
    "left": "left", "start": "left", "both": "left",
}

_PAGE_FIELD_RE = re.compile(r"\bPAGE\b")


def _paragraph_images(paragraph):
    """Ukuran gambar (cm) di dalam paragraf, termasuk gambar melayang."""
    images = []
    for extent in paragraph._p.iter(qn("wp:extent")):
        try:
            images.append({
                "width_cm": round(int(extent.get("cx")) / EMU_PER_CM, 2),
                "height_cm": round(int(extent.get("cy")) / EMU_PER_CM, 2),
            })
        except (TypeError, ValueError):
            continue
    return images


def _page_field_position(element):
    """
    Posisi horizontal nomor halaman (field PAGE) di header/footer,
    "unknown" jika ada tetapi perataannya tidak terbaca, None jika tidak ada.
    """
    if element is None:
        return None
    for p in element.iter(qn("w:p")):
        instr = " ".join(t.text or "" for t in p.iter(qn("w:instrText")))
        instr += " " + " ".join(f.get(qn("w:instr")) or "" for f in p.iter(qn("w:fldSimple")))
        if not _PAGE_FIELD_RE.search(instr.replace("NUMPAGES", "")):
            continue
        frame = p.find(f"{qn('w:pPr')}/{qn('w:framePr')}")
        if frame is not None and frame.get(qn("w:xAlign")):
            return _JC_POSITIONS.get(frame.get(qn("w:xAlign")), "unknown")
        jc = p.find(f"{qn('w:pPr')}/{qn('w:jc')}")
        if jc is not None:
            return _JC_POSITIONS.get(jc.get(qn("w:val")), "unknown")
        return "unknown"
    return None


def _page_numbers(document):
    """
    Nomor halaman tiap section: format (romawi/arab) dan letaknya
    (header = atas, footer = bawah). Header/footer yang tidak ditentukan
    di sebuah section mewarisi section sebelumnya (perilaku Word).
    """
    related = document.part.related_parts
    inherited = {"header": None, "footer": None}
    result = []

    for section in document.sections:
        sect_pr = section._sectPr
        for kind in ("header", "footer"):
            for ref in sect_pr.findall(qn(f"w:{kind}Reference")):
                if ref.get(qn("w:type")) == "default":
                    part = related.get(ref.get(qn("r:id")))
                    inherited[kind] = part.element if part is not None else None

        pg_num = sect_pr.find(qn("w:pgNumType"))
        raw_format = pg_num.get(qn("w:fmt")) if pg_num is not None else None
        header = _page_field_position(inherited["header"])
        footer = _page_field_position(inherited["footer"])

        if header:
            vertical, horizontal = "top", header
        elif footer:
            vertical, horizontal = "bottom", footer
        else:
            vertical = horizontal = None

        result.append({
            "format": _PAGE_FORMATS.get(raw_format or "decimal", raw_format),
            "vertical": vertical,
            "horizontal": horizontal,
        })
    return result


def _iter_paragraphs(document):
    """
    (paragraf, indeks section, di_dalam_tabel) sesuai urutan dokumen,
    TERMASUK paragraf di dalam tabel dan content control (mis. Daftar Isi
    otomatis Word). document.paragraphs melewati keduanya, sehingga dulu
    isi tabel (mis. nama & NPM di sampul) dan daftar isi tidak terbaca.
    """
    body = document._body
    section = 0

    def walk(container, in_table):
        nonlocal section
        for child in container.iterchildren():
            if child.tag == qn("w:p"):
                yield Paragraph(child, body), section, in_table
                if not in_table and child.find(f"{qn('w:pPr')}/{qn('w:sectPr')}") is not None:
                    section += 1
            elif child.tag == qn("w:tbl"):
                for p in child.iter(qn("w:p")):
                    yield Paragraph(p, body), section, True
            elif child.tag == qn("w:sdt"):
                content = child.find(qn("w:sdtContent"))
                if content is not None:
                    yield from walk(content, in_table)

    yield from walk(document.element.body, False)


def parse_docx(file_path):
    """
    Membaca file DOCX dan mengambil informasi
    formatting yang dibutuhkan ThesisFormat.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph, section_index, in_table in _iter_paragraphs(document):
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
                "images": _paragraph_images(paragraph),
                "section_index": section_index,
                # Isi tabel: dibaca untuk sampul & AI, tetapi tidak dinilai
                # sebagai teks isi (tabel memang 10 pt, spasi 1).
                "in_table": in_table,
            }
        )

    sections = []
    page_numbers = _page_numbers(document)

    for index, section in enumerate(document.sections):
        sections.append(
            {
                "top_margin": section.top_margin.cm,
                "bottom_margin": section.bottom_margin.cm,
                "left_margin": section.left_margin.cm,
                "right_margin": section.right_margin.cm,
                "page_width": (
                    round(section.page_width.cm, 2) if section.page_width else None
                ),
                "page_height": (
                    round(section.page_height.cm, 2) if section.page_height else None
                ),
                "page_number": page_numbers[index],
            }
        )

    return {
        "file_name": Path(file_path).name,
        "source_format": "docx",
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