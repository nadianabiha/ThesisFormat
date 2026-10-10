from apps.documents.parser.parser_service import parse_document
from apps.documents.checker.physical_checker import check_physical_rules


def run_jalur_a(file_path, rules=None):
    """
    Jalur A entry point.
    - Parse dokumen (.docx / .pdf)
    - Jika rules tersedia dan hasil parse mendukung checker,
      jalankan physical checker
    - Kembalikan hasil yang siap dipakai backend
    """
    parsed_document = parse_document(file_path)

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