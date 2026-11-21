"""
Aturan tata letak (Pedoman Penulisan Karya Ilmiah Polinela 2018):
ukuran kertas (1.2.1), nomor halaman (1.5.1), ukuran logo (1.3.4), dan
kelengkapan halaman sampul (1.3).

Setiap fungsi menerima (parsed_document, nilai_aturan) dan mengembalikan
{"status", "message", "expected", "found", "chapter"}. Paragraf harus
sudah diberi label bab (chapters.assign_chapters).
"""

import re
from collections import Counter

from .labels import COVER, WHOLE, is_front

FORMAT_LABELS = {
    "roman_lower": "angka romawi kecil (i, ii, iii)",
    "roman_upper": "angka romawi besar (I, II, III)",
    "arabic": "angka Arab (1, 2, 3)",
}
VERTICAL_LABELS = {"top": "atas", "bottom": "bawah"}
HORIZONTAL_LABELS = {"right": "kanan", "center": "tengah", "left": "kiri"}

_NPM_RE = re.compile(r"\b\d{8,12}\b")
_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def _result(status, message, expected, found, chapter=WHOLE):
    return {
        "status": status, "message": message, "expected": expected,
        "found": found, "chapter": chapter,
    }


def _num(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _fmt(value):
    return f"{value:g}".replace(".", ",")


# ---------------------------------------------------------------------------
# Ukuran kertas
# ---------------------------------------------------------------------------

def check_paper_size(parsed, rule):
    width = _num(rule.get("width_cm"), 21.0)
    height = _num(rule.get("height_cm"), 29.7)
    tolerance = _num(rule.get("tolerance_cm"), 0.2)
    expected = {"width_cm": width, "height_cm": height}

    sizes = [
        (p.get("width_cm"), p.get("height_cm")) for p in parsed.get("pages") or []
    ] or [
        (s.get("page_width"), s.get("page_height")) for s in parsed.get("sections") or []
    ]
    sizes = [(w, h) for w, h in sizes if w and h]
    if not sizes:
        return _result("pending", "Ukuran kertas tidak terbaca.", expected, [])

    wrong = []
    for w, h in sizes:
        # Halaman lanskap (diputar) tetap dianggap A4.
        portrait = sorted((w, h))
        if abs(portrait[0] - width) > tolerance or abs(portrait[1] - height) > tolerance:
            wrong.append((round(w, 2), round(h, 2)))

    found = sorted(set(wrong or sizes))
    if wrong:
        w, h = wrong[0]
        message = (
            f"Ukuran kertas {_fmt(w)} × {_fmt(h)} cm, seharusnya A4 "
            f"({_fmt(width)} × {_fmt(height)} cm)."
        )
        if len(wrong) > 1:
            message += f" (Terjadi pada {len(wrong)} bagian/halaman.)"
        return _result("failed", message, expected, found)
    return _result(
        "passed", f"Ukuran kertas sesuai A4 ({_fmt(width)} × {_fmt(height)} cm).",
        expected, found,
    )


# ---------------------------------------------------------------------------
# Nomor halaman
# ---------------------------------------------------------------------------

def _boundaries(paragraphs):
    """Indeks paragraf awal halaman awal (setelah sampul) dan awal bab isi."""
    front_start = next(
        (i for i, p in enumerate(paragraphs) if p.get("chapter") != COVER), None
    )
    body_start = next(
        (i for i, p in enumerate(paragraphs)
         if p.get("chapter") not in (None, WHOLE) and not is_front(p.get("chapter"))),
        None,
    )
    return front_start, body_start


def _docx_groups(parsed, paragraphs, front_start, body_start):
    sections = parsed.get("sections") or []

    def info(index):
        if index is None or index >= len(paragraphs):
            return None
        section_index = paragraphs[index].get("section_index")
        if section_index is None or section_index >= len(sections):
            return None
        return sections[section_index].get("page_number"), section_index

    groups = {}
    front = info(front_start) if front_start is not None and front_start != body_start else None
    body = info(body_start)
    if front:
        groups["front"] = front[0]
    if body:
        groups["body"] = body[0]
    same_section = bool(front and body and front[1] == body[1])
    return groups, same_section


def _majority(values):
    values = [v for v in values if v]
    return Counter(values).most_common(1)[0][0] if values else None


def _pdf_groups(parsed, paragraphs, front_start, body_start):
    labels = {label["page"]: label for label in parsed.get("page_labels") or []}

    def pages(start, end):
        return {p.get("page") for p in paragraphs[start:end] if p.get("page")}

    def summary(page_numbers):
        found = [labels[n] for n in sorted(page_numbers) if n in labels]
        if not found:
            return {"format": None, "vertical": None, "horizontal": None}
        return {
            key: _majority(label[key] for label in found)
            for key in ("format", "vertical", "horizontal")
        }

    groups = {}
    if body_start is not None:
        body_pages = pages(body_start, None)
        if front_start is not None and front_start < body_start:
            front_pages = pages(front_start, body_start) - body_pages
            # Halaman pertama halaman awal biasanya halaman judul dalam.
            if front_pages:
                groups["front"] = summary(front_pages)
        groups["body"] = summary(body_pages)
    return groups, False


def _compare(name, found, expected):
    errors = []
    if not found or not found.get("vertical"):
        return [f"{name}: nomor halaman tidak ditemukan"]
    want_format = expected.get("format")
    if want_format and found.get("format") and found["format"] != want_format:
        errors.append(
            f"{name}: memakai {FORMAT_LABELS.get(found['format'], found['format'])}, "
            f"seharusnya {FORMAT_LABELS.get(want_format, want_format)}"
        )
    want_v, want_h = expected.get("vertical"), expected.get("horizontal")
    v, h = found.get("vertical"), found.get("horizontal")
    wrong_v = want_v and v != want_v
    wrong_h = want_h and h in HORIZONTAL_LABELS and h != want_h
    if wrong_v or wrong_h:
        where = f"{VERTICAL_LABELS.get(v, v)} {HORIZONTAL_LABELS.get(h, '')}".strip()
        should = f"{VERTICAL_LABELS.get(want_v, want_v or '')} {HORIZONTAL_LABELS.get(want_h, '')}".strip()
        errors.append(f"{name}: letaknya di {where}, seharusnya di {should}")
    return errors


def check_page_number(parsed, rule):
    expected = {"front": rule.get("front") or {}, "body": rule.get("body") or {}}
    paragraphs = parsed.get("paragraphs") or []
    front_start, body_start = _boundaries(paragraphs)

    if parsed.get("source_format") == "pdf":
        groups, same_section = _pdf_groups(parsed, paragraphs, front_start, body_start)
        any_number = bool(parsed.get("page_labels"))
    else:
        groups, same_section = _docx_groups(parsed, paragraphs, front_start, body_start)
        any_number = any(
            (s.get("page_number") or {}).get("vertical") for s in parsed.get("sections") or []
        )

    if not any_number:
        return _result(
            "failed", "Dokumen tidak memiliki nomor halaman.", expected, groups,
        )
    if body_start is None:
        return _result(
            "pending",
            "Bab isi (mis. BAB I PENDAHULUAN) tidak terdeteksi, sehingga "
            "penomoran halaman awal dan isi tidak dapat dibedakan.",
            expected, groups,
        )

    errors = []
    if "front" in groups:
        errors += _compare("Halaman awal", groups["front"], expected["front"])
    errors += _compare("Bagian isi", groups.get("body"), expected["body"])

    if errors:
        message = "Nomor halaman tidak sesuai. " + "; ".join(errors) + "."
        if same_section:
            message += (
                " Halaman awal dan bab isi berada di satu section, jadi "
                "penomorannya tidak bisa dibedakan; pisahkan dengan Section Break."
            )
        return _result("failed", message, expected, groups)
    return _result(
        "passed",
        "Nomor halaman sesuai: halaman awal "
        f"{FORMAT_LABELS.get(expected['front'].get('format'), '-')}, bagian isi "
        f"{FORMAT_LABELS.get(expected['body'].get('format'), '-')}.",
        expected, groups,
    )


# ---------------------------------------------------------------------------
# Halaman sampul: logo & kelengkapan
# ---------------------------------------------------------------------------

def _cover(parsed):
    paragraphs = [p for p in parsed.get("paragraphs") or [] if p.get("chapter") == COVER]
    images = [
        image for p in paragraphs for image in p.get("images") or []
        if image.get("width_cm", 0) >= 1 and image.get("height_cm", 0) >= 1
    ]
    text = "\n".join(p.get("text") or "" for p in paragraphs)
    return paragraphs, images, text


def check_logo_size(parsed, rule):
    width = _num(rule.get("width_cm"), 4.0)
    height = _num(rule.get("height_cm"), 3.6)
    tolerance = _num(rule.get("tolerance_cm"), 0.3)
    expected = {"width_cm": width, "height_cm": height, "tolerance_cm": tolerance}

    paragraphs, images, _text = _cover(parsed)
    if not paragraphs:
        return _result(
            "pending", "Halaman sampul tidak terdeteksi, ukuran logo tidak dicek.",
            expected, None, COVER,
        )
    if not images:
        return _result("failed", "Logo tidak ditemukan di halaman sampul.", expected, None, COVER)

    logo = images[0]
    w, h = logo["width_cm"], logo["height_cm"]
    # Bandingkan sisi panjang dengan sisi panjang (logo bisa diputar).
    found_sides = sorted((w, h))
    want_sides = sorted((width, height))
    ok = all(abs(f - e) <= tolerance for f, e in zip(found_sides, want_sides))
    if ok:
        return _result(
            "passed", f"Ukuran logo sesuai ({_fmt(w)} × {_fmt(h)} cm).", expected, logo, COVER,
        )
    return _result(
        "failed",
        f"Ukuran logo {_fmt(w)} × {_fmt(h)} cm, seharusnya {_fmt(width)} × "
        f"{_fmt(height)} cm (toleransi ±{_fmt(tolerance)} cm).",
        expected, logo, COVER,
    )


COVER_ELEMENTS = {
    "logo": "logo Polinela",
    "npm": "nama dan NPM penulis",
    "institusi": "nama institusi (Politeknik Negeri Lampung)",
    "tahun": "tahun",
}


def check_cover(parsed, rule):
    required = [key for key in rule.get("required") or list(COVER_ELEMENTS) if key in COVER_ELEMENTS]
    institution = str(rule.get("institution") or "POLITEKNIK NEGERI LAMPUNG")
    expected = {"required": required, "institution": institution}

    paragraphs, images, text = _cover(parsed)
    if not paragraphs:
        return _result(
            "pending", "Halaman sampul tidak terdeteksi, kelengkapan sampul tidak dicek.",
            expected, None, COVER,
        )

    compact = re.sub(r"\s+", " ", text).upper()
    present = {
        "logo": bool(images),
        "npm": bool(_NPM_RE.search(text)),
        "institusi": re.sub(r"\s+", " ", institution).upper() in compact,
        "tahun": bool(_YEAR_RE.search(text)),
    }
    missing = [key for key in required if not present[key]]
    found = {key: present[key] for key in required}
    if missing:
        return _result(
            "failed",
            "Halaman sampul belum lengkap. Belum ada: "
            + ", ".join(COVER_ELEMENTS[key] for key in missing) + ".",
            expected, found, COVER,
        )
    return _result(
        "passed",
        "Halaman sampul lengkap: " + ", ".join(COVER_ELEMENTS[key] for key in required) + ".",
        expected, found, COVER,
    )


LAYOUT_CHECKS = {
    "paper_size": check_paper_size,
    "page_number": check_page_number,
    "logo_size": check_logo_size,
    "cover": check_cover,
}
