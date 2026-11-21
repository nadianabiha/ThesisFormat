"""
Tes Jalur A: pembaca PDF, pembagian bab, dan aturan tata letak
(ukuran kertas, nomor halaman, logo, kelengkapan sampul).
File DOCX/PDF contoh dibuat di dalam tes, jadi tidak butuh file luar.
"""

import io
import os
import shutil
import tempfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from docx import Document as Docx
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image
from rest_framework.test import APITestCase

from apps.documents.checker.chapters import assign_chapters, match_chapter
from apps.documents.checker.layout_checks import (
    check_cover,
    check_logo_size,
    check_page_number,
    check_paper_size,
)
from apps.documents.parser.jalur_a_service import run_jalur_a
from apps.documents.parser.pdf_parser import normalize_font, parse_pdf
from apps.documents.scoring import normalize_physical, normalize_semantic

PAGE_RULE = {
    "front": {"format": "roman_lower", "vertical": "bottom", "horizontal": "right"},
    "body": {"format": "arabic", "vertical": "top", "horizontal": "right"},
}
BODY = (
    "Penelitian ini membahas rancangan sistem pemeriksa format karya ilmiah "
    "yang membantu mahasiswa memperbaiki dokumen sebelum bimbingan dosen."
)


def _png(path):
    Image.new("RGB", (40, 36), "navy").save(path)


def _page_field(paragraph, align):
    """Sisipkan field PAGE (nomor halaman Word) ke paragraf header/footer."""
    paragraph.alignment = align
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), " PAGE ")
    paragraph._p.append(field)


def _set_format(section, fmt):
    # add_section menyalin pengaturan section sebelumnya; hapus dulu.
    for old in section._sectPr.findall(qn("w:pgNumType")):
        section._sectPr.remove(old)
    pg = OxmlElement("w:pgNumType")
    if fmt:
        pg.set(qn("w:fmt"), fmt)
    section._sectPr.append(pg)


def make_docx(folder, logo_cm=(4, 3.6), with_numbers=True, npm_in_table=True):
    doc = Docx()
    first = doc.sections[0]
    first.page_width, first.page_height = Cm(21), Cm(29.7)

    # Sampul
    image = os.path.join(folder, "logo.png")
    _png(image)
    doc.add_paragraph("RANCANG BANGUN SISTEM THESISFORMAT").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().add_run().add_picture(image, width=Cm(logo_cm[0]), height=Cm(logo_cm[1]))
    if npm_in_table:
        table = doc.add_table(rows=1, cols=2)
        table.cell(0, 0).text = "Yuri Elva"
        table.cell(0, 1).text = "24782097"
    doc.add_paragraph("POLITEKNIK NEGERI LAMPUNG")
    doc.add_paragraph("2026")

    # Halaman awal (section 2: romawi kecil, kanan bawah)
    front = doc.add_section(WD_SECTION.NEW_PAGE)
    front.footer.is_linked_to_previous = False
    if with_numbers:
        _page_field(front.footer.paragraphs[0], WD_ALIGN_PARAGRAPH.RIGHT)
    _set_format(front, "lowerRoman")
    heading = doc.add_paragraph()
    heading.add_run("KATA PENGANTAR").bold = True
    doc.add_paragraph(BODY)

    # Bab isi (section 3: angka Arab, kanan atas)
    body = doc.add_section(WD_SECTION.NEW_PAGE)
    body.footer.is_linked_to_previous = False
    body.header.is_linked_to_previous = False
    if with_numbers:
        _page_field(body.header.paragraphs[0], WD_ALIGN_PARAGRAPH.RIGHT)
    _set_format(body, None)
    for title in ("BAB I PENDAHULUAN", "BAB II TINJAUAN PUSTAKA"):
        run = doc.add_paragraph().add_run(title)
        run.bold = True
        paragraph = doc.add_paragraph(BODY)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    path = os.path.join(folder, "contoh.docx")
    doc.save(path)
    return path


def make_pdf(path, pages):
    """
    PDF teks sederhana (font Times-Roman) tanpa library tambahan.
    pages: daftar halaman, tiap halaman daftar (x_cm, y_cm_dari_atas, ukuran, teks).
    """
    width, height = 595.28, 841.89  # A4 dalam point
    objects = []

    def add(body):
        objects.append(body)
        return len(objects)

    font = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >>")
    pages_id = len(objects) + 2 * len(pages) + 1
    kids = []
    for lines in pages:
        stream = io.BytesIO()
        for x_cm, y_cm, size, text in lines:
            x = x_cm * 72 / 2.54
            y = height - y_cm * 72 / 2.54
            safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            stream.write(f"BT /F1 {size} Tf {x:.2f} {y:.2f} Td ({safe}) Tj ET\n".encode("latin-1"))
        data = stream.getvalue()
        content = add(b"<< /Length %d >>\nstream\n" % len(data) + data + b"\nendstream")
        kids.append(add(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {width} {height}] "
            f"/Resources << /Font << /F1 {font} 0 R >> >> /Contents {content} 0 R >>".encode()
        ))
    add(f"<< /Type /Pages /Kids [{' '.join(f'{k} 0 R' for k in kids)}] /Count {len(kids)} >>".encode())
    catalog = add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())

    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(f"{number} 0 obj\n".encode() + body + b"\nendobj\n")
    xref = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets:
        out.write(f"{offset:010d} 00000 n \n".encode())
    out.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    )
    with open(path, "wb") as handle:
        handle.write(out.getvalue())


def _wrapped(text, start_y, x=4, words_per_line=11, spacing_cm=0.73):
    """Baris-baris paragraf rata kiri-kanan, spasi 1,5 (20,7 pt ≈ 0,73 cm)."""
    words = text.split()
    lines = []
    for index in range(0, len(words), words_per_line):
        lines.append((x, start_y + len(lines) * spacing_cm, 12, " ".join(words[index:index + words_per_line])))
    return lines


class DocxLayoutTests(SimpleTestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)

    def _parsed(self, **kwargs):
        from apps.documents.parser.docx_parser import parse_docx

        parsed = parse_docx(make_docx(self.folder, **kwargs))
        parsed["chapters"] = assign_chapters(parsed["paragraphs"])
        return parsed

    def test_chapters_and_cover_table_are_read(self):
        parsed = self._parsed()
        self.assertEqual(parsed["chapters"], ["KATA PENGANTAR", "BAB I PENDAHULUAN", "BAB II TINJAUAN PUSTAKA"])
        cover = [p for p in parsed["paragraphs"] if p["chapter"] == "Halaman sampul"]
        # NPM ditulis di tabel sampul: dulu tidak terbaca sama sekali.
        self.assertTrue(any("24782097" in p["text"] and p["in_table"] for p in cover))

    def test_layout_rules_pass_for_correct_document(self):
        parsed = self._parsed()
        self.assertEqual(check_paper_size(parsed, {})["status"], "passed")
        self.assertEqual(check_logo_size(parsed, {})["status"], "passed")
        self.assertEqual(check_cover(parsed, {})["status"], "passed")
        result = check_page_number(parsed, PAGE_RULE)
        self.assertEqual(result["status"], "passed", result["message"])

    def test_big_logo_and_missing_numbers_fail(self):
        parsed = self._parsed(logo_cm=(6.6, 6.8), with_numbers=False)
        logo = check_logo_size(parsed, {})
        self.assertEqual(logo["status"], "failed")
        self.assertIn("6,6", logo["message"])
        self.assertEqual(logo["chapter"], "Halaman sampul")
        self.assertEqual(check_page_number(parsed, PAGE_RULE)["status"], "failed")

    def test_wrong_page_number_position_is_reported(self):
        parsed = self._parsed()
        rule = {**PAGE_RULE, "body": {"format": "arabic", "vertical": "bottom", "horizontal": "center"}}
        result = check_page_number(parsed, rule)
        self.assertEqual(result["status"], "failed")
        self.assertIn("Bagian isi", result["message"])

    def test_cover_without_npm_fails(self):
        parsed = self._parsed(npm_in_table=False)
        result = check_cover(parsed, {})
        self.assertEqual(result["status"], "failed")
        self.assertIn("NPM", result["message"])

    def test_physical_findings_carry_chapter(self):
        path = make_docx(self.folder)
        rules = {
            "line_spacing": {"value": 2.0, "scope": "body"},
            "logo_size": {"value": {"width_cm": 4, "height_cm": 3.6}},
        }
        doc = Docx(path)
        for paragraph in doc.paragraphs:
            if paragraph.text == BODY:
                paragraph.paragraph_format.line_spacing = 1.5
        doc.save(path)

        items = normalize_physical(run_jalur_a(path, rules=rules)["findings"])
        spacing = next(i for i in items if i["rule_key"] == "line_spacing")
        self.assertEqual(spacing["status"], "failed")
        self.assertIn("Terjadi di:", spacing["detail"])
        self.assertIn("BAB I PENDAHULUAN", spacing["chapters"])
        logo = next(i for i in items if i["rule_key"] == "logo_size")
        self.assertEqual(logo["chapter"], "Halaman sampul")


class PdfParserTests(SimpleTestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)
        self.path = os.path.join(self.folder, "contoh.pdf")
        long_text = (BODY + " ") * 3
        make_pdf(self.path, [
            [(7, 4, 14, "RANCANG BANGUN SISTEM THESISFORMAT"), (8, 12, 12, "Yuri Elva 24782097"),
             (7, 20, 12, "POLITEKNIK NEGERI LAMPUNG"), (10, 21, 12, "2026")],
            [(8, 3, 14, "KATA PENGANTAR"), *_wrapped(long_text, 5), (17.5, 28, 12, "ii")],
            [(8, 3, 14, "BAB I PENDAHULUAN"), *_wrapped(long_text, 5), (17.5, 1.5, 12, "1")],
        ])

    def test_pdf_has_paragraphs_chapters_and_page_numbers(self):
        parsed = parse_pdf(self.path)
        self.assertTrue(parsed["layout_estimated"])
        self.assertGreater(len(parsed["paragraphs"]), 3)
        chapters = assign_chapters(parsed["paragraphs"])
        self.assertIn("BAB I PENDAHULUAN", chapters)

        fonts = {r["font_name"] for p in parsed["paragraphs"] for r in p["runs"]}
        self.assertEqual(fonts, {"Times New Roman"})
        self.assertEqual(parsed["sections"][0]["page_width"], 21.0)

        labels = {label["text"]: label for label in parsed["page_labels"]}
        self.assertEqual(labels["ii"]["format"], "roman_lower")
        self.assertEqual((labels["ii"]["vertical"], labels["ii"]["horizontal"]), ("bottom", "right"))
        self.assertEqual(labels["1"]["vertical"], "top")

        parsed["chapters"] = chapters
        result = check_page_number(parsed, PAGE_RULE)
        self.assertEqual(result["status"], "passed", result["message"])

    def test_pdf_text_reaches_ai(self):
        """Dulu PDF selalu gagal dengan "Teks dokumen tidak terbaca"."""
        from apps.documents.semantic import jalur_b_service

        parsed = run_jalur_a(self.path, rules={})["parsed_document"]
        with mock.patch.object(
            jalur_b_service, "generate_with_fallback", return_value=('{"findings": []}', "m"),
        ) as generate:
            result = jalur_b_service.run_jalur_b(parsed)
        self.assertNotEqual(result["error_type"], "no_text")
        self.assertIn("Penelitian ini membahas", generate.call_args[0][0])

    def test_normalize_font(self):
        self.assertEqual(normalize_font("ABCDEF+TimesNewRomanPS-BoldItalicMT"), ("Times New Roman", True, True))
        self.assertEqual(normalize_font("TimesNewRomanPSMT"), ("Times New Roman", False, False))
        self.assertEqual(normalize_font("Arial-BoldMT"), ("Arial", True, False))


class ChapterFindingTests(SimpleTestCase):

    def test_ai_chapter_is_matched_to_document_chapters(self):
        chapters = ["KATA PENGANTAR", "BAB I PENDAHULUAN", "BAB II TINJAUAN PUSTAKA"]
        self.assertEqual(match_chapter("bab i pendahuluan", chapters), "BAB I PENDAHULUAN")
        self.assertEqual(match_chapter("TINJAUAN PUSTAKA", chapters), "BAB II TINJAUAN PUSTAKA")
        self.assertEqual(match_chapter("Bab yang tidak ada", chapters), "Seluruh dokumen")
        self.assertEqual(match_chapter("", chapters), "Seluruh dokumen")

    def test_ai_findings_get_chapter_and_list_answer_is_accepted(self):
        from apps.documents.semantic import jalur_b_service

        parsed = {
            "paragraphs": [{"text": "teks", "runs": []}],
            "chapters": ["BAB I PENDAHULUAN"],
        }
        # Jawaban AI berupa daftar langsung (bukan {"findings": [...]}).
        answer = '[{"category": "sitasi", "status": "failed", "chapter": "BAB I", "issue": "a"}]'
        with mock.patch.object(jalur_b_service, "generate_with_fallback", return_value=(answer, "m")) as gen:
            result = jalur_b_service.run_jalur_b(parsed)
        self.assertIsNone(result["error"])
        self.assertEqual(result["findings"][0]["chapter"], "BAB I PENDAHULUAN")
        self.assertIn('"BAB I PENDAHULUAN"', gen.call_args[0][0])

    def test_old_findings_without_chapter_go_to_whole_document(self):
        item = normalize_semantic([{"category": "sitasi", "status": "failed", "issue": "x"}])[0]
        self.assertEqual(item["chapter"], "Seluruh dokumen")
        physical = normalize_physical([{"rule_key": "margin", "status": "failed", "message": "m"}])[0]
        self.assertEqual(physical["chapter"], "Seluruh dokumen")
        self.assertEqual(physical["location"], "Dokumen")


class UploadValidationTests(APITestCase):
    """Jenis & ukuran file dicek di server, bukan hanya di aplikasi."""

    def setUp(self):
        user = get_user_model().objects.create_user(username="mhs_upload", password="rahasia123")
        self.client.force_authenticate(user)

    def _upload(self, name, content):
        return self.client.post(
            "/api/v1/documents/upload/",
            {"file": SimpleUploadedFile(name, content), "document_type": "pkl"},
            format="multipart",
        )

    def test_wrong_extension_is_rejected_with_clear_message(self):
        response = self._upload("virus.exe", b"x")
        self.assertEqual(response.status_code, 400)
        self.assertIn(".pdf atau .docx", response.data["detail"])

    @override_settings(MAX_UPLOAD_MB=1)
    def test_too_large_file_is_rejected(self):
        response = self._upload("besar.docx", b"x" * (1024 * 1024 + 10))
        self.assertEqual(response.status_code, 400)
        self.assertIn("1 MB", response.data["detail"])
