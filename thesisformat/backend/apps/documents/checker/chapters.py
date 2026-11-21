"""
Pembagian dokumen per bab.

Setiap paragraf diberi label bab ("chapter"), misalnya "Halaman sampul",
"KATA PENGANTAR", "BAB I PENDAHULUAN", "DAFTAR PUSTAKA". Label ini dipakai
untuk menampilkan kesalahan per bab (Laporan Perancangan) dan dikirim ke AI
agar AI menyebut bab tempat setiap masalah.
"""

import re

from .labels import COVER, FRONT, FRONT_TITLES, WHOLE
from .physical_checker import _CAPTION_RE, _cover_end_index, _is_heading_like

# Judul bagian (bukan bab bernomor) yang menjadi pembatas bab.
_SECTION_TITLES = FRONT_TITLES + ("DAFTAR PUSTAKA", "LAMPIRAN", "PENDAHULUAN")

_CHAPTER_STYLES = ("heading 1", "judul 1")

# Bagian berisi daftar dengan nomor halaman di ujung baris (daftar isi, dll.).
_LIST_SECTIONS = ("DAFTAR ISI", "DAFTAR TABEL", "DAFTAR GAMBAR", "DAFTAR LAMPIRAN")

_BAB_RE = re.compile(r"^BAB\s+([IVXLC]+|\d+)\b\.?\s*(.*)$", re.IGNORECASE)
_ROMAN_TITLE_RE = re.compile(r"^([IVXLC]+)\.\s+(\S.*)$")
# "1. PENDAHULUAN" (bukan subbab "1.1 ...").
_ARABIC_TITLE_RE = re.compile(r"^(\d{1,2})\.?\s+([^\d\s].*)$")
# Baris daftar isi diakhiri nomor halaman: angka Arab atau romawi KECIL
# ("BAB I PENDAHULUAN ..... 1", "KATA PENGANTAR iii"). Romawi besar di
# akhir ("BAB I") adalah judul bab, bukan nomor halaman.
_TOC_LINE_RE = re.compile(r"((\.{3,}|…|\t)\s*\S+|\s(\d+|[ivxlc]+))\s*$")


def _clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def _is_upper(text):
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def _number_value(number):
    if number.isdigit():
        return int(number)
    total = 0
    values = [_ROMAN_VALUES.get(c, 0) for c in number.upper()]
    for value, following in zip(values, values[1:] + [0]):
        total += -value if value < following else value
    return total


def _small_text(paragraph):
    """Teks kecil (isi tabel/keterangan, < 12 pt) bukan judul bab."""
    sizes = [r.get("font_size") for r in paragraph.get("runs", []) if r.get("font_size")]
    return bool(sizes) and max(sizes) < 12


def chapter_title(paragraph, next_texts=()):
    """
    (nama bab, nomor bab) jika paragraf ini judul bab, selain itu None.
    next_texts: teks paragraf sesudahnya, untuk judul "BAB I" yang
    namanya ditulis di baris berikutnya ("PENDAHULUAN").
    """
    text = _clean(paragraph.get("text"))
    if (
        not text or len(text.split()) > 12 or paragraph.get("in_table")
        or not _is_heading_like(paragraph) or _small_text(paragraph)
        or _CAPTION_RE.match(text)
    ):
        return None

    match = _BAB_RE.match(text)
    if match:
        number, name = match.group(1).upper(), _clean(match.group(2))
        if not name:
            name = next((t for t in next_texts if t and _is_upper(t)), "")
        return _clean(f"BAB {number} {name.upper()}"), _number_value(number)

    match = _ROMAN_TITLE_RE.match(text) or _ARABIC_TITLE_RE.match(text)
    if match and _is_upper(match.group(2)) and re.search(r"[A-Z]{4}", match.group(2)):
        number = match.group(1)
        return _clean(f"BAB {number} {match.group(2).upper()}"), _number_value(number)

    upper = text.upper().rstrip(".:")
    if _is_upper(text):
        if upper.startswith("LAMPIRAN"):
            return "LAMPIRAN", None
        for title in _SECTION_TITLES:
            if upper == title or upper.startswith(title + " "):
                return upper, None

    # Judul bab dengan style "Heading 1" dan nomor otomatis Word (nomornya
    # tidak ada di teks, mis. "PROJECT OVERVIEW").
    style = (paragraph.get("style") or "").strip().lower()
    if style in _CHAPTER_STYLES:
        return upper, None
    return None


def assign_chapters(paragraphs):
    """
    Tambahkan kunci "chapter" pada setiap paragraf (dict) dan kembalikan
    daftar nama bab sesuai urutan kemunculan.
    """
    paragraphs = [p for p in paragraphs if isinstance(p, dict)]
    cover_end = _cover_end_index(paragraphs)
    current = COVER if cover_end > 0 else FRONT
    chapters = []
    skip_next = False
    last_number = 0

    for index, paragraph in enumerate(paragraphs):
        if index < cover_end:
            paragraph["chapter"] = COVER
            continue

        text = _clean(paragraph.get("text"))
        if skip_next and text:
            # Baris nama bab sesudah "BAB I" sudah digabung ke judul.
            skip_next = False
            if _is_upper(text) and _BAB_RE.match(current or "") and current.endswith(text.upper()):
                paragraph["chapter"] = current
                continue

        # Baris di daftar isi ("BAB I PENDAHULUAN .... 1") bukan judul bab.
        raw = paragraph.get("text") or ""
        in_list = current in _LIST_SECTIONS
        toc_line = bool(_TOC_LINE_RE.search(text)) or "\t" in raw or "...." in raw
        title = None
        if not (in_list and toc_line and text.upper() not in _LIST_SECTIONS):
            following = [
                _clean(p.get("text")) for p in paragraphs[index + 1:index + 3]
            ]
            found = chapter_title(paragraph, following)
            if found:
                title, number = found
                # Bab bernomor harus berurutan (I, II, III); nomor yang
                # melompat jauh biasanya isi tabel/daftar, bukan judul bab.
                if number is not None:
                    if last_number < number <= last_number + 2:
                        last_number = number
                    else:
                        title = None

        if title:
            current = title
            if title not in chapters:
                chapters.append(title)
            skip_next = bool(_BAB_RE.match(text)) and not _clean(_BAB_RE.match(text).group(2))
        paragraph["chapter"] = current

    if not chapters:
        # Tidak ada judul bab yang dikenali: dokumen dianggap satu bagian.
        for paragraph in paragraphs:
            if paragraph.get("chapter") == FRONT:
                paragraph["chapter"] = WHOLE
    return chapters


def match_chapter(raw, chapters):
    """Cocokkan nama bab dari AI ke daftar bab dokumen; selain itu WHOLE."""
    text = _clean(str(raw or "")).upper()
    if not text:
        return WHOLE
    for name in (COVER, FRONT, WHOLE):
        if text == name.upper():
            return name
    for chapter in chapters:
        if text == chapter.upper():
            return chapter
    # "BAB II" atau "TINJAUAN PUSTAKA" saja tetap dikenali.
    for chapter in chapters:
        upper = chapter.upper()
        if upper.startswith(text + " ") or upper.endswith(" " + text) or text.startswith(upper):
            return chapter
    return WHOLE
