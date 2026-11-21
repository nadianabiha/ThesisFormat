"""Label bab bersama (dipakai pembagian bab, pemeriksa format, dan AI)."""

COVER = "Halaman sampul"
FRONT = "Halaman awal"
WHOLE = "Seluruh dokumen"

# Judul bagian halaman awal (sebelum bab isi pertama).
FRONT_TITLES = (
    "ABSTRAK", "ABSTRACT", "RINGKASAN", "SUMMARY", "KATA PENGANTAR", "PRAKATA",
    "SANWACANA", "UCAPAN TERIMA KASIH", "PERSEMBAHAN", "MOTTO", "RIWAYAT HIDUP",
    "HALAMAN PENGESAHAN", "LEMBAR PENGESAHAN", "PENGESAHAN", "PERNYATAAN",
    "DAFTAR ISI", "DAFTAR TABEL", "DAFTAR GAMBAR", "DAFTAR LAMPIRAN",
)


def is_front(chapter):
    """True jika label bab termasuk sampul/halaman awal."""
    if not chapter or chapter in (COVER, FRONT):
        return True
    upper = chapter.upper()
    return any(upper == t or upper.startswith(t + " ") for t in FRONT_TITLES)
