import json
import os
import re
import time

import httpx
from google.genai import errors

from apps.documents.checker.chapters import match_chapter
from apps.documents.scoring import normalize_category, normalize_severity
from apps.documents.semantic.gemini_client import (
    GEMINI_MODELS,
    GEMINI_TIMEOUT_SECONDS,
    generate,
)
from apps.documents.semantic.prompts import MAX_TEXT_CHARS, build_semantic_prompt

# Kode error Gemini yang bersifat sementara (sibuk, kuota, timeout server).
TRANSIENT_CODES = {429, 500, 502, 503, 504}

# Batas total waktu untuk semua percobaan (detik). Model cadangan hanya
# dicoba jika sisa waktu masih cukup untuk satu panggilan penuh, agar
# upload tidak menggantung terlalu lama. Tetap di bawah batas tunggu
# "Cek ulang" di app (4 menit). Di server di belakang Cloudflare (batas
# 100 detik per permintaan) isi AI_TOTAL_BUDGET_SECONDS=70 di .env.
try:
    TOTAL_BUDGET_SECONDS = max(10, int(os.getenv("AI_TOTAL_BUDGET_SECONDS", "180")))
except ValueError:
    TOTAL_BUDGET_SECONDS = 180

# Jenis penyebab kegagalan AI (dipakai halaman "Kinerja AI").
ERROR_LABELS = {
    "unavailable": "Gemini sedang sibuk (503)",
    "timeout": "Waktu habis (504/timeout)",
    "quota": "Kuota API habis (429)",
    "connection": "Koneksi internet terputus",
    "config": "API key/model tidak valid",
    "no_text": "Teks dokumen tidak terbaca",
    "invalid_response": "Respons AI tidak sesuai format",
    "other": "Lainnya",
}


def _is_transient(exc):
    if isinstance(exc, errors.APIError):
        return getattr(exc, "code", None) in TRANSIENT_CODES
    # Timeout dari sisi kita, atau koneksi terputus.
    return isinstance(exc, httpx.TransportError)


def classify_error(exc):
    """Kelompokkan error menjadi salah satu kunci ERROR_LABELS."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        if code == 503 or code in (500, 502):
            return "unavailable"
        if code == 504:
            return "timeout"
        if code == 429:
            return "quota"
        if code in (400, 401, 403, 404):
            return "config"
        return "other"
    if isinstance(exc, httpx.TimeoutException):
        return "timeout"
    if isinstance(exc, httpx.TransportError):
        return "connection"
    if isinstance(exc, (json.JSONDecodeError, ValueError)):
        return "invalid_response"
    return "other"


def generate_with_fallback(prompt, models=None):
    """
    Panggil Gemini dengan model utama; jika sibuk/timeout, pindah
    ke model cadangan. Error lain (mis. API key salah) langsung dilempar.
    Mengembalikan (teks, nama model yang berhasil menjawab).
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
            return generate(prompt, model=model), model

        except Exception as exc:
            # Model tidak ada/dihapus Google (404): coba model berikutnya.
            model_missing = (
                isinstance(exc, errors.APIError) and getattr(exc, "code", None) == 404
            )
            if not (_is_transient(exc) or model_missing):
                raise

            last_exc = exc
            print(f"Gemini {model} gagal ({type(exc).__name__}): {exc}")

            # Tanpa koneksi internet, model lain juga pasti gagal.
            if isinstance(exc, httpx.ConnectError):
                break

    if last_exc is None:
        raise ValueError("Tidak ada model Gemini yang dikonfigurasi.")
    raise last_exc


def generate_with_retry(prompt, models=None):
    """Sama seperti generate_with_fallback, tetapi hanya mengembalikan teks."""
    text, _model = generate_with_fallback(prompt, models)
    return text


def _empty_result(error, error_type, started, model=""):
    return {
        "raw_response": "",
        "findings": [],
        "summary": {"passed": 0, "failed": 0, "total": 0},
        "error": error,
        "error_type": error_type,
        "model": model,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "unknown_categories": [],
    }


def paragraph_text_with_italics(paragraph):
    """
    Teks paragraf dengan penanda huruf miring: bagian yang dicetak miring di
    dokumen asli dibungkus "_..._", agar AI bisa menilai apakah istilah asing
    sudah dimiringkan (AI hanya menerima teks polos).
    """
    text = paragraph.get("text") or ""
    runs = [r for r in paragraph.get("runs") or [] if isinstance(r, dict)]
    if not any(r.get("italic") for r in runs):
        return text
    # Pakai run hanya jika isinya sama dengan teks paragraf (tidak ada
    # teks yang hilang, mis. dari hyperlink/field).
    if "".join(r.get("text") or "" for r in runs).strip() != text.strip():
        return text

    parts = []
    italic_buffer = []

    def flush():
        chunk = "".join(italic_buffer)
        if chunk.strip():
            # Spasi di tepi tetap di luar penanda: "_database_ ".
            lead = chunk[: len(chunk) - len(chunk.lstrip())]
            trail = chunk[len(chunk.rstrip()):]
            parts.append(f"{lead}_{chunk.strip()}_{trail}")
        else:
            parts.append(chunk)
        italic_buffer.clear()

    for run in runs:
        if run.get("italic"):
            italic_buffer.append(run.get("text") or "")
        else:
            flush()
            parts.append(run.get("text") or "")
    flush()
    return "".join(parts)


def run_jalur_b(parsed_document, document_type=None, aspects=None):
    """
    Menganalisis isi dokumen menggunakan Gemini.
    Jika Gemini gagal, kembalikan error tanpa menghentikan
    pemeriksaan fisik Jalur A.

    aspects: aspek aktif beserta instruksinya (dari MasterRule semantic).
    Hasil juga mencatat model, durasi, dan jenis error untuk
    halaman "Kinerja AI" di dashboard.
    """
    started = time.monotonic()

    paragraphs = parsed_document.get("paragraphs", [])
    full_text = "\n".join(
        text
        for text in (
            paragraph_text_with_italics(paragraph)
            for paragraph in paragraphs
            if isinstance(paragraph, dict)
        )
        if text.strip()
    ).strip()

    if not full_text:
        return _empty_result(
            "Tidak ada teks yang berhasil diekstrak dari dokumen.",
            "no_text",
            started,
        )

    # Dicatat agar terlihat jika dokumen terlalu panjang dan sebagian
    # tidak ikut dibaca AI.
    text_info = {
        "text_chars": len(full_text),
        "text_truncated": len(full_text) > MAX_TEXT_CHARS,
    }
    chapters = parsed_document.get("chapters") or []
    prompt = build_semantic_prompt(full_text, document_type, aspects, chapters)
    allowed = None if aspects is None else {a["key"] for a in aspects}

    raw_response = ""
    model = ""

    try:
        raw_response, model = generate_with_fallback(prompt)

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
        # Sebagian model menjawab langsung berupa daftar [...] alih-alih
        # {"findings": [...]}; keduanya diterima.
        raw_findings = parsed if isinstance(parsed, list) else parsed.get("findings", [])

        if not isinstance(raw_findings, list):
            raise ValueError("Format findings dari Gemini tidak valid.")

        findings = []
        unknown = set()

        for item in raw_findings:
            if not isinstance(item, dict):
                continue

            issue = str(item.get("issue", "")).strip()
            if not issue:
                continue

            raw_category = str(item.get("category", "")).strip()
            category = normalize_category(raw_category)
            if not category:
                unknown.add(raw_category or "(kosong)")
            elif allowed is not None and category not in allowed:
                # Aspek dinonaktifkan admin: abaikan.
                continue

            status_value = str(item.get("status", "")).lower().strip()
            status = "passed" if status_value == "passed" else "failed"

            finding = {
                "category": category,
                "issue": issue,
                "location": str(
                    item.get("location") or "Lokasi tidak diketahui"
                ),
                "status": status,
                "chapter": match_chapter(item.get("chapter"), chapters),
            }
            if status == "failed":
                # Tingkat kesalahan dari AI (ringan/sedang/berat) menentukan
                # besar potongan nilai; tanpa ini semua dianggap "sedang".
                finding["severity"] = normalize_severity(item.get("severity"))
            findings.append(finding)

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
            "error": None,
            "error_type": "",
            "model": model,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "unknown_categories": sorted(unknown),
            **text_info,
        }

    except Exception as exc:
        # Kegagalan Gemini tidak perlu menghentikan seluruh proses upload.
        print(f"Analisis Jalur B gagal: {exc}")

        result = _empty_result(str(exc), classify_error(exc), started, model)
        result["raw_response"] = raw_response
        result.update(text_info)
        return result
