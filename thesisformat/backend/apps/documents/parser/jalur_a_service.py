from apps.documents.parser.parser_service import parse_document
from apps.documents.checker.chapters import assign_chapters
from apps.documents.checker.physical_checker import check_physical_rules


def extract_document(file_path):
    """
    Ekstraksi teks & metadata dokumen (.docx / .pdf), dilakukan SEKALI
    lalu hasilnya dipakai bersama oleh Jalur A dan Jalur B yang berjalan
    paralel (Laporan Perancangan D.3).
    """
    parsed_document = parse_document(file_path)
    # Label bab per paragraf: untuk menampilkan kesalahan per bab,
    # membedakan halaman awal/isi (nomor halaman), dan dikirim ke AI.
    parsed_document["chapters"] = assign_chapters(parsed_document.get("paragraphs", []))
    return parsed_document


def run_jalur_a(file_path, rules=None, parsed_document=None):
    """
    Jalur A entry point.
    - Pakai hasil ekstraksi (parsed_document) jika sudah ada; jika tidak,
      ekstrak dokumen dulu (.docx / .pdf)
    - Jika rules tersedia dan hasil parse mendukung checker,
      jalankan physical checker
    - Kembalikan hasil yang siap dipakai backend
    Hanya MEMBACA parsed_document, sehingga aman berjalan bersamaan
    dengan Jalur B.
    """
    if parsed_document is None:
        parsed_document = extract_document(file_path)

    findings = []
    checker_applied = False

    # Checker fisik saat ini memakai struktur paragraphs + sections
    # jadi hanya dijalankan jika struktur itu ada.
    if rules and "paragraphs" in parsed_document and "sections" in parsed_document:
        findings = check_physical_rules(parsed_document, rules)
        checker_applied = True

    passed_count = sum(1 for item in findings if item["status"] == "passed")
    failed_count = sum(1 for item in findings if item["status"] == "failed")
    pending_count = sum(1 for item in findings if item["status"] == "pending")

    return {
        "parsed_document": parsed_document,
        "checker_applied": checker_applied,
        "findings": findings,
        "summary": {
            "passed": passed_count,
            "failed": failed_count,
            "pending": pending_count,
            "total": len(findings),
        },
    }