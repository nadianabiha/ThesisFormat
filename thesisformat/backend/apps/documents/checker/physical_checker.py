import re

# ---------------------------------------------------------------------------
# Teks isi vs judul/tabel (Pedoman Penulisan Karya Ilmiah Polinela 2018)
# - Teks isi: Times New Roman 12, spasi 1,5, rata kiri-kanan (1.4).
# - Judul bab: 14 pt, tebal, rata tengah, spasi 1 (1.4.1b, 2.2.2).
# - Isi & keterangan tabel/gambar: 10 pt, spasi 1 (1.4.1c-d).
# - Abstrak/ringkasan, daftar isi/tabel/gambar, daftar pustaka: spasi 1.
# Karena itu ukuran font, perataan, dan spasi hanya dicek pada TEKS ISI.
# ---------------------------------------------------------------------------

# Cakupan bawaan tiap aturan: "body" = teks isi saja, "all" = semua paragraf.
DEFAULT_SCOPE = {
    "font_name": "all",
    "font_size": "body",
    "alignment": "body",
    "line_spacing": "body",
}

_HEADING_STYLE_PREFIXES = (
    "heading", "judul", "title", "subtitle", "caption", "toc",
    "table of figures", "daftar",
)

# Bagian yang menurut panduan tidak memakai format teks isi.
_NON_BODY_SECTIONS = (
    "ABSTRAK", "ABSTRACT", "RINGKASAN", "SUMMARY",
    "DAFTAR ISI", "DAFTAR TABEL", "DAFTAR GAMBAR", "DAFTAR LAMPIRAN",
    "DAFTAR PUSTAKA", "LAMPIRAN", "HALAMAN PENGESAHAN", "PENGESAHAN",
    "RIWAYAT HIDUP", "PERSEMBAHAN", "SANWACANA", "MOTTO",
)

_CAPTION_RE = re.compile(r"^\s*(tabel|gambar|table|figure)\s+\d", re.IGNORECASE)
_NUMBERING_RE = re.compile(r"^\s*((BAB\s+)?[IVXLC]+\.?|\d+(\.\d+)*\.?)\s+", re.IGNORECASE)

# Judul bagian yang menandai akhir halaman sampul/judul. Semua paragraf
# sebelum judul pertama dari daftar ini dianggap sampul (rata tengah dan
# berukuran besar secara wajar), jadi tidak dicek sebagai teks isi.
_FIRST_SECTION_STARTS = _NON_BODY_SECTIONS + (
    "KATA PENGANTAR", "PRAKATA", "PERNYATAAN", "LEMBAR PENGESAHAN",
    "UCAPAN TERIMA KASIH", "BAB", "PENDAHULUAN", "LATAR BELAKANG",
)

# Paragraf dengan kata lebih sedikit dari ini dianggap bukan teks isi
# (baris sampul, nama, tanda tangan, butir pendek).
_MIN_BODY_WORDS = 8


def _is_heading_like(paragraph):
    """Judul bab/subbab: memakai style judul, atau pendek & kapital/tebal."""
    style = (paragraph.get("style") or "").strip().lower()
    if style.startswith(_HEADING_STYLE_PREFIXES):
        return True

    text = (paragraph.get("text") or "").strip()
    words = len(text.split())
    if not text or words > 15:
        return False

    letters = [char for char in text if char.isalpha()]
    if letters and all(char.isupper() for char in letters):
        return True

    runs = [run for run in paragraph.get("runs", []) if (run.get("text") or "").strip()]
    return bool(runs) and all(run.get("bold") for run in runs)


def _section_name(text):
    return _NUMBERING_RE.sub("", text.upper()).strip()


def _cover_end_index(paragraphs):
    """
    Indeks judul bagian pertama setelah halaman sampul. Bila tidak ada
    judul yang dikenali, dianggap tidak ada sampul (0) agar dokumen tetap
    diperiksa.
    """
    for index, paragraph in enumerate(paragraphs):
        text = (paragraph.get("text") or "").strip()
        if not text or not _is_heading_like(paragraph):
            continue
        if text.upper().startswith("BAB") or _section_name(text).startswith(_FIRST_SECTION_STARTS):
            return index
    return 0


def _body_paragraphs(parsed_document):
    """
    Paragraf teks isi: bukan halaman sampul, bukan judul, bukan judul
    tabel/gambar, bukan baris pendek, dan tidak berada di bagian yang
    memakai spasi satu (abstrak, daftar isi, daftar pustaka, lampiran, dll.).
    """
    body = []
    section = ""
    paragraphs = parsed_document.get("paragraphs", [])

    for paragraph in paragraphs[_cover_end_index(paragraphs):]:
        text = (paragraph.get("text") or "").strip()
        if not text:
            continue

        if _is_heading_like(paragraph):
            section = _section_name(text)
            continue

        if section.startswith(_NON_BODY_SECTIONS):
            continue
        if _CAPTION_RE.match(text):
            continue
        if len(text.split()) < _MIN_BODY_WORDS:
            continue

        body.append(paragraph)

    return body


def _target_paragraphs(parsed_document, rule_key, rule_value):
    """Paragraf yang diperiksa sesuai cakupan aturan (styles / scope)."""
    styles = rule_value.get("styles")
    if styles:
        return _get_target_paragraphs(parsed_document, styles), "styles"

    scope = rule_value.get("scope") or DEFAULT_SCOPE.get(rule_key, "all")
    if scope == "body":
        return _body_paragraphs(parsed_document), "body"
    return parsed_document.get("paragraphs", []), "all"


_MARGIN_LABELS = {
    "top_margin": "atas",
    "bottom_margin": "bawah",
    "left_margin": "kiri",
    "right_margin": "kanan",
}


def _scope_prefix(scope):
    return "Teks isi: " if scope == "body" else ""


def _get_rule_value(rule_value):
    if isinstance(rule_value, dict):
        return rule_value.get("value", rule_value)
    return rule_value


def _cm_close(found, expected, tolerance=0.05):
    try:
        return abs(float(found) - float(expected)) <= tolerance
    except (TypeError, ValueError):
        return False


def _get_target_paragraphs(parsed_document, styles=None):
    paragraphs = parsed_document.get("paragraphs", [])

    if not styles:
        return paragraphs

    if isinstance(styles, str):
        styles = [styles]

    return [
        paragraph
        for paragraph in paragraphs
        if paragraph.get("style") in styles
    ]


def check_physical_rules(parsed_document, rules):
    """
    Memeriksa format fisik dokumen berdasarkan MasterRule.

    Mendukung rules berbentuk dictionary:
    {
        "font_name": {"value": "Times New Roman"},
        "font_size": {"value": 12}
    }
    """

    findings = []

    # Backend mengirim rules sebagai dictionary dengan rule_key
    # sebagai key dan rule_value sebagai value.
    if isinstance(rules, dict):
        rule_items = rules.items()
    else:
        # Mendukung juga daftar objek MasterRule.
        rule_items = (
            (rule.rule_key, rule.rule_value)
            for rule in rules
        )

    for rule_key, rule_value in rule_items:
        if not isinstance(rule_value, dict):
            rule_value = {"value": rule_value}

        # ==========================================
        # RULE: FONT NAME
        # ==========================================
        if rule_key == "font_name":
            expected_font = rule_value.get("value")
            target_paragraphs, scope = _target_paragraphs(
                parsed_document, rule_key, rule_value
            )

            found_fonts = {
                run.get("font_name")
                for paragraph in target_paragraphs
                for run in paragraph.get("runs", [])
                if run.get("font_name")
            }

            if not found_fonts:
                status = "pending"
                message = (
                    "Informasi font tidak ditemukan secara eksplisit "
                    "pada hasil parsing dokumen."
                )
            else:
                invalid_fonts = [
                    font for font in found_fonts
                    if font != expected_font
                ]

                if invalid_fonts:
                    status = "failed"
                    message = (
                        f"{_scope_prefix(scope)}Font tidak sesuai. Ditemukan: "
                        f"{', '.join(sorted(invalid_fonts))}. "
                        f"Seharusnya: {expected_font}."
                    )
                else:
                    status = "passed"
                    message = (
                        f"Semua font yang terbaca sesuai dengan "
                        f"aturan {expected_font}."
                    )

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_font,
                "found": sorted(found_fonts),
            })

        # ==========================================
        # RULE: FONT SIZE
        # ==========================================
        elif rule_key == "font_size":
            expected_size = rule_value.get("value")
            target_paragraphs, scope = _target_paragraphs(
                parsed_document, rule_key, rule_value
            )

            found_sizes = {
                run.get("font_size")
                for paragraph in target_paragraphs
                for run in paragraph.get("runs", [])
                if run.get("font_size") is not None
            }

            if not found_sizes:
                status = "pending"
                message = (
                    "Informasi ukuran font tidak ditemukan secara "
                    "eksplisit pada hasil parsing dokumen."
                )
            else:
                invalid_sizes = [
                    size for size in found_sizes
                    if not _cm_close(size, expected_size, tolerance=0.01)
                ]

                if invalid_sizes:
                    status = "failed"
                    message = (
                        f"{_scope_prefix(scope)}Ukuran font tidak sesuai. Ditemukan: "
                        f"{', '.join(map(str, sorted(invalid_sizes)))} pt. "
                        f"Seharusnya: {expected_size} pt."
                    )
                else:
                    status = "passed"
                    message = (
                        f"Semua ukuran font yang terbaca sesuai "
                        f"dengan aturan {expected_size} pt."
                    )

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_size,
                "found": sorted(found_sizes),
            })

        # ==========================================
        # RULE: ALIGNMENT
        # ==========================================
        elif rule_key == "alignment":
            expected_alignment = rule_value.get("value")
            target_paragraphs, scope = _target_paragraphs(
                parsed_document, rule_key, rule_value
            )

            found_alignments = {
                paragraph.get("alignment")
                for paragraph in target_paragraphs
                if paragraph.get("alignment")
            }

            if not found_alignments:
                status = "pending"
                message = (
                    "Informasi alignment tidak ditemukan secara "
                    "eksplisit pada hasil parsing dokumen."
                )
            else:
                invalid_alignments = [
                    alignment for alignment in found_alignments
                    if alignment != expected_alignment
                ]

                if invalid_alignments:
                    status = "failed"
                    message = (
                        f"{_scope_prefix(scope)}Perataan tidak sesuai. Ditemukan: "
                        f"{', '.join(sorted(invalid_alignments))}. "
                        f"Seharusnya: {expected_alignment}."
                    )
                else:
                    status = "passed"
                    message = (
                        f"Semua alignment yang terbaca sesuai "
                        f"dengan aturan {expected_alignment}."
                    )

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_alignment,
                "found": sorted(found_alignments),
            })

        # ==========================================
        # RULE: LINE SPACING
        # ==========================================
        elif rule_key == "line_spacing":
            expected_spacing = rule_value.get("value")
            target_paragraphs, scope = _target_paragraphs(
                parsed_document, rule_key, rule_value
            )

            found_spacings = {
                paragraph.get("line_spacing")
                for paragraph in target_paragraphs
                if paragraph.get("line_spacing") is not None
                and isinstance(
                    paragraph.get("line_spacing"), (int, float)
                )
                and not isinstance(paragraph.get("line_spacing"), bool)
                and paragraph.get("line_spacing") <= 5
            }

            if not found_spacings:
                status = "pending"
                message = (
                    "Informasi line spacing numerik tidak ditemukan "
                    "pada hasil parsing dokumen."
                )
            else:
                invalid_spacings = [
                    spacing for spacing in found_spacings
                    if not _cm_close(
                        spacing, expected_spacing, tolerance=0.01
                    )
                ]

                if invalid_spacings:
                    status = "failed"
                    message = (
                        f"{_scope_prefix(scope)}Spasi baris tidak sesuai. Ditemukan: "
                        f"{', '.join(map(str, sorted(invalid_spacings)))}. "
                        f"Seharusnya: {expected_spacing}."
                    )
                else:
                    status = "passed"
                    message = (
                        f"Semua line spacing yang terbaca sesuai "
                        f"dengan aturan {expected_spacing}."
                    )

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_spacing,
                "found": sorted(found_spacings),
            })

        # ==========================================
        # RULE: MARGIN
        # ==========================================
        elif rule_key == "margin":
            expected_margin = _get_rule_value(rule_value)

            if not isinstance(expected_margin, dict):
                findings.append({
                    "rule_key": rule_key,
                    "status": "pending",
                    "message": "Konfigurasi rule margin belum valid.",
                    "expected": rule_value,
                    "found": None,
                })
                continue

            found_sections = parsed_document.get("sections", [])

            if not found_sections:
                findings.append({
                    "rule_key": rule_key,
                    "status": "pending",
                    "message": "Informasi margin tidak ditemukan.",
                    "expected": expected_margin,
                    "found": [],
                })
                continue

            invalid_sections = []

            for index, section in enumerate(found_sections, start=1):
                section_errors = []

                for margin_key in (
                    "top_margin",
                    "bottom_margin",
                    "left_margin",
                    "right_margin",
                ):
                    expected = expected_margin.get(margin_key)
                    found = section.get(margin_key)

                    if (
                        expected is not None
                        and not _cm_close(found, expected)
                    ):
                        found_text = (
                            f"{float(found):.2f}".replace(".", ",")
                            if isinstance(found, (int, float)) else found
                        )
                        section_errors.append(
                            f"{_MARGIN_LABELS[margin_key]} {found_text} cm, "
                            f"seharusnya {expected} cm"
                        )

                if section_errors:
                    invalid_sections.append({
                        "section": index,
                        "errors": section_errors,
                        "found": section,
                    })

            if invalid_sections:
                status = "failed"
                errors = invalid_sections[0]["errors"]
                message = "Margin tidak sesuai: " + "; ".join(errors) + "."
                if len(invalid_sections) > 1:
                    message += (
                        f" (Terjadi pada {len(invalid_sections)} bagian dokumen.)"
                    )
            else:
                status = "passed"
                message = (
                    "Margin sesuai aturan (atas "
                    f"{expected_margin.get('top_margin')}, kanan "
                    f"{expected_margin.get('right_margin')}, bawah "
                    f"{expected_margin.get('bottom_margin')}, kiri "
                    f"{expected_margin.get('left_margin')} cm)."
                )

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_margin,
                "found": (
                    invalid_sections if invalid_sections else found_sections
                ),
            })

        # ==========================================
        # RULE LAINNYA
        # ==========================================
        else:
            findings.append({
                "rule_key": rule_key,
                "status": "pending",
                "message": (
                    f"Rule '{rule_key}' belum memiliki "
                    "logika pemeriksaan."
                ),
                "expected": rule_value,
                "found": None,
            })

    return findings
