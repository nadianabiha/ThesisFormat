"""
Pembaca PDF untuk Jalur A dan Jalur B.

PDF tidak menyimpan "paragraf" seperti Word, hanya posisi setiap kata.
Karena itu paragraf, perataan, spasi, dan margin di sini DISUSUN ULANG
dari posisi teks, sehingga sifatnya perkiraan (layout_estimated=True).
Hasilnya berbentuk sama dengan parse_docx agar pemeriksaan format dan AI
berjalan untuk kedua jenis file.
"""

import re
from collections import Counter
from pathlib import Path
from statistics import median

import pdfplumber

PT_PER_CM = 72 / 2.54

# Satu spasi Word untuk Times New Roman ≈ 1,15 × ukuran font.
_SINGLE_LINE_FACTOR = 1.15
_STANDARD_SPACINGS = (1.0, 1.15, 1.5, 2.0)

# Pita atas/bawah halaman tempat nomor halaman biasanya berada.
_PAGE_NUMBER_BAND_CM = 3.2
_PAGE_NUMBER_RE = re.compile(r"^(\d{1,4}|[ivxlcdm]{1,7}|[IVXLCDM]{1,7})$")

_SPECIAL_FONT_RE = re.compile(r"math|symbol|wingdings|webdings|^_", re.IGNORECASE)

_FONT_ALIASES = {
    "Times": "Times New Roman",
    "TimesNewRoman": "Times New Roman",
    "TimesNewRomanPS": "Times New Roman",
}


def _cm(points):
    return round(points / PT_PER_CM, 2)


def normalize_font(raw):
    """
    Nama font PDF -> nama font seperti di Word, plus tebal/miring.
    "ABCDEF+TimesNewRomanPS-BoldItalicMT" -> ("Times New Roman", True, True)
    """
    name = str(raw or "").split("+")[-1]
    bold = bool(re.search(r"bold|black|heavy|semibold", name, re.IGNORECASE))
    italic = bool(re.search(r"italic|oblique", name, re.IGNORECASE))
    base = re.split(r"[-,]", name)[0]
    base = re.sub(r"(PSMT|PS|MT)$", "", base)
    if base in _FONT_ALIASES:
        return _FONT_ALIASES[base], bold, italic
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", base).strip()
    return spaced or None, bold, italic


def _number_format(text):
    if text.isdigit():
        return "arabic"
    return "roman_lower" if text.islower() else "roman_upper"


def _horizontal(x0, x1, width):
    center = (x0 + x1) / 2
    if center > width * 0.62:
        return "right"
    if center < width * 0.38:
        return "left"
    return "center"


def _group_lines(words):
    """Kelompokkan kata menjadi baris berdasarkan posisi vertikal."""
    lines = []
    for word in sorted(words, key=lambda w: (round(w["top"]), w["x0"])):
        if lines and abs(word["top"] - lines[-1]["top"]) <= 2.5:
            lines[-1]["words"].append(word)
        else:
            lines.append({"top": word["top"], "words": [word]})

    for line in lines:
        line["words"].sort(key=lambda w: w["x0"])
        line["x0"] = min(w["x0"] for w in line["words"])
        line["x1"] = max(w["x1"] for w in line["words"])
        line["bottom"] = max(w["bottom"] for w in line["words"])
        line["text"] = " ".join(w["text"] for w in line["words"])
        sizes = Counter(round(w["size"] * 2) / 2 for w in line["words"])
        line["size"] = sizes.most_common(1)[0][0]
        line["bold"] = all(normalize_font(w["fontname"])[1] for w in line["words"])
        # Celah lebar antar kata = kolom tabel tanpa garis.
        gaps = [b["x0"] - a["x1"] for a, b in zip(line["words"], line["words"][1:])]
        line["multi_column"] = bool(gaps) and max(gaps) > 1.2 * PT_PER_CM
    return lines


def _mode(values, step=0.5 * PT_PER_CM / 5):
    """Nilai yang paling sering muncul (dibulatkan ke kelipatan step)."""
    if not values:
        return None
    rounded = Counter(round(v / step) * step for v in values)
    return rounded.most_common(1)[0][0]


def _alignment(lines, left, right):
    tolerance = 0.35 * PT_PER_CM
    if len(lines) >= 2:
        body = lines[:-1]
        if all(right - line["x1"] <= tolerance for line in body):
            return "JUSTIFY" if all(line["x0"] - left <= 1.6 * PT_PER_CM for line in body) else "RIGHT"
    centered = all(
        abs((line["x0"] - left) - (right - line["x1"])) <= 0.4 * PT_PER_CM
        and line["x0"] - left > 0.5 * PT_PER_CM
        for line in lines
    )
    if centered:
        return "CENTER"
    if len(lines) >= 2:
        return "LEFT"
    # Satu baris: rata kiri, rata kanan-kiri, dan baris terakhir paragraf
    # tidak bisa dibedakan, jadi tidak dinilai.
    return None


def _line_spacing(lines):
    if len(lines) < 2:
        return None
    gaps = [b["bottom"] - a["bottom"] for a, b in zip(lines, lines[1:]) if b["bottom"] > a["bottom"]]
    if not gaps:
        return None
    size = median(line["size"] for line in lines) or 12
    ratio = median(gaps) / (size * _SINGLE_LINE_FACTOR)
    if ratio < 0.9:
        return None  # baris bertumpuk (sel tabel), bukan spasi teks
    nearest = min(_STANDARD_SPACINGS, key=lambda s: abs(s - ratio))
    return nearest if abs(nearest - ratio) <= 0.12 else round(ratio, 2)


def _build_runs(lines):
    """Run = kata-kata berurutan dengan font, ukuran, tebal, miring yang sama."""
    words = [w for line in lines for w in line["words"]]
    runs = []
    for index, word in enumerate(words):
        font, bold, italic = normalize_font(word["fontname"])
        size = round(word["size"] * 2) / 2
        text = word["text"] + (" " if index < len(words) - 1 else "")
        if not any(c.isalnum() for c in word["text"]) or _SPECIAL_FONT_RE.search(font or ""):
            # Simbol, bullet, dan rumus memakai font khusus (Symbol,
            # Cambria Math, font tersemat Word), bukan font teks.
            font = None
        key = (font, size, bold, italic)
        if runs and runs[-1]["_key"] == key:
            runs[-1]["text"] += text
        else:
            runs.append({
                "_key": key, "text": text, "font_name": font, "font_size": size,
                "bold": bold, "italic": italic, "underline": None,
            })
    for run in runs:
        run.pop("_key")
    return runs


def _starts_new_paragraph(prev, line, left, right, gap):
    if prev is None:
        return True
    if line["in_table"] != prev["in_table"]:
        return True
    if line["in_table"] and line["bottom"] - prev["bottom"] > (gap or 14) * 1.2:
        return True  # baris tabel yang berjauhan = sel/baris tabel lain
    if abs(line["size"] - prev["size"]) > 0.6 or line["bold"] != prev["bold"]:
        return True  # judul vs teks isi
    if prev["page"] != line["page"]:
        # Paragraf berlanjut ke halaman berikutnya hanya jika baris
        # terakhir halaman sebelumnya penuh dan baris ini tidak menjorok.
        return not (
            right - prev["x1"] <= 1.0 * PT_PER_CM
            and line["x0"] - left <= 0.3 * PT_PER_CM
        )
    if gap and line["bottom"] - prev["bottom"] > gap * 1.45:
        return True
    if right - prev["x1"] > 1.0 * PT_PER_CM:
        return True  # baris sebelumnya pendek = akhir paragraf
    if line["x0"] - left > 0.4 * PT_PER_CM and abs(line["x0"] - prev["x0"]) > 0.2 * PT_PER_CM:
        return True  # baris menjorok = awal paragraf baru
    return False


def parse_pdf(file_path):
    """
    Membaca file PDF dan menyusun paragraf, ukuran halaman, margin
    (perkiraan), nomor halaman, dan gambar.
    """
    pages = []
    page_labels = []
    all_lines = []
    total_text = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            band = _PAGE_NUMBER_BAND_CM * PT_PER_CM

            words = page.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False)
            lines = _group_lines(words)
            # Baris di dalam tabel ditandai: dibaca untuk sampul & AI, tetapi
            # tidak dinilai sebagai teks isi (sama seperti DOCX).
            tables = [table.bbox for table in page.find_tables()]
            for line in lines:
                cx, cy = (line["x0"] + line["x1"]) / 2, (line["top"] + line["bottom"]) / 2
                line["in_table"] = line["multi_column"] or any(
                    x0 <= cx <= x1 and top <= cy <= bottom for x0, top, x1, bottom in tables
                )
            total_text.append("\n".join(line["text"] for line in lines))
            label = None
            body_lines = []
            for line in lines:
                in_band = line["bottom"] < band or line["top"] > page.height - band
                if in_band and _PAGE_NUMBER_RE.match(line["text"].strip()) and label is None:
                    label = {
                        "page": page_number,
                        "text": line["text"].strip(),
                        "format": _number_format(line["text"].strip()),
                        "vertical": "top" if line["bottom"] < band else "bottom",
                        "horizontal": _horizontal(line["x0"], line["x1"], page.width),
                    }
                    continue
                line["page"] = page_number
                body_lines.append(line)
            if label:
                page_labels.append(label)

            images = [
                {"width_cm": _cm(img["x1"] - img["x0"]), "height_cm": _cm(img["bottom"] - img["top"])}
                for img in page.images
                if (img["x1"] - img["x0"]) > PT_PER_CM and (img["bottom"] - img["top"]) > PT_PER_CM
            ]
            pages.append({
                "page_number": page_number,
                "text": total_text[-1],
                "width": page.width,
                "height": page.height,
                "width_cm": _cm(page.width),
                "height_cm": _cm(page.height),
                "images": images,
                "_lines": body_lines,
            })
            all_lines.extend(body_lines)

    # Tepi teks yang paling sering = batas margin kiri/kanan.
    left = _mode([line["x0"] for line in all_lines]) or 0
    right = _mode([line["x1"] for line in all_lines]) or 0
    gaps = [
        b["bottom"] - a["bottom"]
        for a, b in zip(all_lines, all_lines[1:])
        if a["page"] == b["page"] and b["bottom"] > a["bottom"]
    ]
    gap = median(gaps) if gaps else None

    # Susun paragraf dari baris.
    groups = []
    prev = None
    for line in all_lines:
        if _starts_new_paragraph(prev, line, left, right, gap):
            groups.append([line])
        else:
            groups[-1].append(line)
        prev = line

    paragraphs = []
    first_on_page = set()
    for lines in groups:
        runs = _build_runs(lines)
        page_number = lines[0]["page"]
        images = []
        if page_number not in first_on_page:
            first_on_page.add(page_number)
            images = pages[page_number - 1]["images"]
        paragraphs.append({
            "text": "".join(run["text"] for run in runs),
            "style": None,
            "alignment": _alignment(lines, left, right),
            "line_spacing": _line_spacing(lines),
            "space_before": None,
            "space_after": None,
            "first_line_indent": None,
            "runs": runs,
            "images": images,
            "page": page_number,
            "section_index": 0,
            "in_table": all(line["in_table"] for line in lines),
        })

    # Margin perkiraan dari posisi teks (persentil agar tidak terpengaruh
    # satu-dua baris yang menyimpang).
    def _percentile(values, fraction):
        values = sorted(values)
        return values[int((len(values) - 1) * fraction)] if values else None

    first_tops = [p["_lines"][0]["top"] for p in pages if p["_lines"]]
    last_gaps = [p["height"] - p["_lines"][-1]["bottom"] for p in pages if p["_lines"]]
    width = pages[0]["width"] if pages else 0
    sections = []
    if all_lines:
        sections.append({
            "top_margin": _cm(_percentile(first_tops, 0.1)),
            "bottom_margin": _cm(_percentile(last_gaps, 0.1)),
            "left_margin": _cm(left),
            "right_margin": _cm(width - right),
            "page_width": pages[0]["width_cm"],
            "page_height": pages[0]["height_cm"],
            "page_number": None,
        })

    for page in pages:
        page.pop("_lines")

    return {
        "file_name": Path(file_path).name,
        "source_format": "pdf",
        "layout_estimated": True,
        "page_count": len(pages),
        "text": "\n".join(total_text),
        "pages": pages,
        "page_labels": page_labels,
        "paragraphs": paragraphs,
        "sections": sections,
        "paragraph_count": len(paragraphs),
    }
