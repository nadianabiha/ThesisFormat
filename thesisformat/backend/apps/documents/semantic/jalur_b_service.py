import json
import re
import time

from google.genai import errors
from apps.documents.semantic.gemini_client import generate
from apps.documents.semantic.prompts import build_semantic_prompt


def generate_with_retry(prompt, max_retries=3):
    """
    Mencoba ulang permintaan Gemini jika server sedang bermasalah.
    """
    for attempt in range(max_retries):
        try:
            return generate(prompt)

        except errors.ServerError as exc:
            # Coba ulang hanya untuk error server sementara.
            if getattr(exc, "code", None) not in (429, 500, 502, 503, 504):
                raise

            if attempt == max_retries - 1:
                raise

            delay = 2 ** (attempt + 1)
            print(
                f"Gemini sedang bermasalah. "
                f"Mencoba ulang dalam {delay} detik..."
            )
            time.sleep(delay)


def run_jalur_b(parsed_document, document_type=None):
    """
    Menganalisis isi dokumen menggunakan Gemini.
    Jika Gemini gagal, kembalikan error tanpa menghentikan
    pemeriksaan fisik Jalur A.
    """

    paragraphs = parsed_document.get("paragraphs", [])
    full_text = " ".join(
        paragraph.get("text", "")
        for paragraph in paragraphs
        if isinstance(paragraph, dict)
    ).strip()

    if not full_text:
        return {
            "raw_response": "",
            "findings": [],
            "summary": {
                "passed": 0,
                "failed": 0,
                "total": 0,
            },
            "error": "Tidak ada teks yang berhasil diekstrak dari dokumen.",
        }

    prompt = build_semantic_prompt(full_text, document_type)

    raw_response = ""

    try:
        raw_response = generate_with_retry(prompt)

        if not isinstance(raw_response, str) or not raw_response.strip():
            raise ValueError("Gemini tidak memberikan respons teks.")

        cleaned = raw_response.strip()
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*```$", "", cleaned)

        parsed = json.loads(cleaned)
        raw_findings = parsed.get("findings", [])

        if not isinstance(raw_findings, list):
            raise ValueError("Format findings dari Gemini tidak valid.")

        findings = []

        for item in raw_findings:
            if not isinstance(item, dict):
                continue

            issue = str(item.get("issue", "")).strip()
            if not issue:
                continue

            status_value = str(item.get("status", "")).lower().strip()
            status = "passed" if status_value == "passed" else "failed"

            findings.append({
                "category": str(item.get("category", "")).strip().lower(),
                "issue": issue,
                "location": str(
                    item.get("location") or "Lokasi tidak diketahui"
                ),
                "status": status,
            })

        passed_count = sum(
            1 for item in findings if item["status"] == "passed"
        )
        failed_count = sum(
            1 for item in findings if item["status"] == "failed"
        )

        return {
            "raw_response": raw_response,
            "findings": findings,
            "summary": {
                "passed": passed_count,
                "failed": failed_count,
                "total": len(findings),
            },
        }

    except Exception as exc:
        # Kegagalan Gemini tidak perlu menghentikan seluruh proses upload.
        print(f"Analisis Jalur B gagal: {exc}")

        return {
            "raw_response": raw_response,
            "findings": [],
            "summary": {
                "passed": 0,
                "failed": 0,
                "total": 0,
            },
            "error": str(exc),
        }