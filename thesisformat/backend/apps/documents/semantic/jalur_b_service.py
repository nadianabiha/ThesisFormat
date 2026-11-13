import json
import re
import time

import httpx
from google.genai import errors

from apps.documents.semantic.gemini_client import (
    GEMINI_MODELS,
    GEMINI_TIMEOUT_SECONDS,
    generate,
)
from apps.documents.semantic.prompts import build_semantic_prompt

# Kode error Gemini yang bersifat sementara (sibuk, kuota, timeout server).
TRANSIENT_CODES = {429, 500, 502, 503, 504}

# Batas total waktu untuk semua percobaan (detik). Model cadangan hanya
# dicoba jika sisa waktu masih cukup untuk satu panggilan penuh, agar
# upload tidak menggantung terlalu lama.
TOTAL_BUDGET_SECONDS = 150


def _is_transient(exc):
    if isinstance(exc, errors.APIError):
        return getattr(exc, "code", None) in TRANSIENT_CODES
    # Timeout dari sisi kita, atau koneksi terputus.
    return isinstance(exc, httpx.TransportError)


def generate_with_retry(prompt, models=None):
    """
    Panggil Gemini dengan model utama; jika sibuk/timeout, pindah
    ke model cadangan. Error lain (mis. API key salah) langsung dilempar.
    """
    models = models or GEMINI_MODELS
    started = time.monotonic()
    last_exc = None

    for index, model in enumerate(models):
        if index > 0:
            elapsed = time.monotonic() - started
            if elapsed + GEMINI_TIMEOUT_SECONDS > TOTAL_BUDGET_SECONDS:
                break
            time.sleep(1)

        try:
            return generate(prompt, model=model)

        except Exception as exc:
            if not _is_transient(exc):
                raise

            last_exc = exc
            print(f"Gemini {model} gagal ({type(exc).__name__}): {exc}")

            # Tanpa koneksi internet, model lain juga pasti gagal.
            if isinstance(exc, httpx.ConnectError):
                break

    if last_exc is None:
        raise ValueError("Tidak ada model Gemini yang dikonfigurasi.")
    raise last_exc


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