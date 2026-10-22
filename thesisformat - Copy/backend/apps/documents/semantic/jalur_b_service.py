from apps.documents.semantic.gemini_client import generate


def run_jalur_b(parsed_document, document_type=None):
    """
    Jalur B entry point.
    - Ambil teks dari hasil parse Jalur A (parsed_document)
    - Kirim ke Gemini untuk dicek secara semantik
    - Kembalikan hasil dengan bentuk yang sama seperti run_jalur_a
    """
    full_text = " ".join(
        paragraph["text"] for paragraph in parsed_document.get("paragraphs", [])
    )

    prompt = f"""
    Kamu adalah pemeriksa format {document_type or "karya tulis ilmiah"}.
    Analisis teks berikut, cek konsistensi sitasi, struktur, dan tata bahasa.
    Balas HANYA dalam format JSON seperti ini:
    {{"findings": [{{"issue": "...", "location": "...", "status": "failed"}}]}}

    Teks: {full_text[:3000]}
    """

    raw_response = generate(prompt)

    # untuk sekarang findings masih kosong dulu sampai parsing JSON-nya siap
    findings = []

    passed_count = sum(1 for item in findings if item["status"] == "passed")
    failed_count = sum(1 for item in findings if item["status"] == "failed")

    return {
        "raw_response": raw_response,
        "findings": findings,
        "summary": {
            "passed": passed_count,
            "failed": failed_count,
            "total": len(findings),
        },
    }