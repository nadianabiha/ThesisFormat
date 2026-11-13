"""
Perhitungan skor dan normalisasi temuan.

Skor dihitung di backend (satu sumber kebenaran) agar Flutter hanya
menampilkan data, sesuai API_CONTRACT_FRONTEND.md.
"""

# Sesuai Laporan Perancangan: 40% aspek fisik + 60% aspek semantik.
FORMAT_WEIGHT = 0.4
SEMANTIC_WEIGHT = 0.6

SEMANTIC_CATEGORIES = {
    "sitasi": "Sitasi & kepustakaan",
    "daftar_isi": "Daftar isi, tabel, gambar & lampiran",
    "hierarki_bab": "Hierarki & urutan bab",
    "abstrak": "Abstrak",
    "tata_bahasa": "Tata bahasa & istilah asing",
    "benang_merah": "Benang merah penelitian",
    "konsistensi_istilah": "Konsistensi istilah teknis",
}

_TYPE_BY_STATUS = {
    "passed": "success",
    "failed": "error",
    "pending": "warning",
}


def _pct(passed, failed):
    checked = passed + failed
    if checked == 0:
        return None
    return round(passed / checked * 100)


def normalize_physical(findings):
    """Ubah temuan Jalur A ke bentuk yang seragam untuk UI."""
    items = []
    for f in findings or []:
        status = f.get("status", "pending")
        items.append({
            "source": "physical",
            "status": status,
            "type": _TYPE_BY_STATUS.get(status, "warning"),
            "title": str(f.get("rule_key", "aturan")).replace("_", " "),
            "location": "Dokumen",
            "detail": f.get("message", ""),
        })
    return items


def normalize_semantic(findings):
    """Ubah temuan Jalur B ke bentuk yang seragam untuk UI."""
    items = []
    for f in findings or []:
        status = "passed" if f.get("status") == "passed" else "failed"
        category = f.get("category") or ""
        items.append({
            "source": "semantic",
            "category": category,
            "status": status,
            "type": _TYPE_BY_STATUS[status],
            "title": SEMANTIC_CATEGORIES.get(category, "Isi & struktur"),
            "location": f.get("location") or "Lokasi tidak diketahui",
            "detail": f.get("issue", ""),
        })
    return items


def physical_score(findings):
    """Persentase aturan fisik lulus. 'pending' tidak dihitung."""
    passed = sum(1 for f in findings if f.get("status") == "passed")
    failed = sum(1 for f in findings if f.get("status") == "failed")
    return _pct(passed, failed)


def semantic_score(findings):
    """
    Persentase aspek semantik yang lulus. Satu aspek (kategori) dianggap
    gagal jika punya minimal satu temuan 'failed'.
    """
    by_category = {}
    for f in findings:
        category = f.get("category")
        if not category:
            continue
        failed = f.get("status") == "failed"
        by_category[category] = by_category.get(category, False) or failed

    if not by_category:
        return None
    passed = sum(1 for failed in by_category.values() if not failed)
    return _pct(passed, len(by_category) - passed)


def build_result(jalur_a, jalur_b):
    """Bangun hasil akhir (skor + temuan) dari output Jalur A dan B."""
    physical = normalize_physical(jalur_a.get("findings", []))
    semantic = normalize_semantic(jalur_b.get("findings", []))

    format_score = physical_score(physical)
    sem_score = semantic_score(semantic)

    if format_score is not None and sem_score is not None:
        total = round(FORMAT_WEIGHT * format_score + SEMANTIC_WEIGHT * sem_score)
    elif format_score is not None:
        total = format_score
    elif sem_score is not None:
        total = sem_score
    else:
        total = 0

    return {
        "total_score": total,
        "format_score": format_score or 0,
        "semantic_score": sem_score or 0,
        "has_format_score": format_score is not None,
        "has_semantic_score": sem_score is not None,
        "findings": physical + semantic,
        "semantic_error": jalur_b.get("error"),
    }


def result_from_metadata(metadata):
    """Hitung hasil dari metadata lama (dokumen yang diunggah sebelum perbaikan)."""
    metadata = metadata or {}
    jalur_a = metadata.get("jalur_a") or {}
    jalur_b = metadata.get("jalur_b") or {}
    if not jalur_a and not jalur_b:
        return None
    return build_result(jalur_a, jalur_b)
