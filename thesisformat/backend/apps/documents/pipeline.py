"""
Alur pemeriksaan dokumen (Laporan Perancangan D.3):
ekstraksi dokumen -> Jalur A (fisik) & Jalur B (AI) PARALEL -> skor.

Dipakai oleh upload mahasiswa (DocumentUploadView) dan "Analisis ulang"
admin (Web Dashboard), sehingga keduanya memakai aturan & instruksi AI
yang sama, dan setiap analisis AI tercatat di AIRun.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor

from apps.audits.models import AIRun, AuditResult
from apps.rules.models import MasterRule, RuleVersion

from .parser.jalur_a_service import extract_document, run_jalur_a
from .scoring import build_result
from .semantic.jalur_b_service import run_jalur_b

logger = logging.getLogger(__name__)


def _ms_since(started):
    return round((time.monotonic() - started) * 1000)


def check_document(document, trigger=AIRun.Trigger.UPLOAD, user=None):
    """
    Jalankan pemeriksaan lengkap lalu simpan hasilnya.
    Mengembalikan dict: jalur_a, jalur_b, result, findings, summary, ai_run.
    Error Jalur A (mis. file tidak terbaca) dilempar ke pemanggil.
    """
    rule_version = RuleVersion.current()
    started = time.monotonic()

    # Semua data dari database diambil di sini (sebelum paralel), sehingga
    # kedua jalur di bawah tidak menyentuh database dari thread lain.
    physical_rules = MasterRule.for_document(
        MasterRule.Category.PHYSICAL,
        document.document_type,
    )
    aspects = MasterRule.semantic_aspects(document.document_type)
    document_type_label = document.get_document_type_display()

    # 1. Ekstraksi teks & metadata, sekali untuk kedua jalur.
    #    Error (mis. file tidak terbaca) dilempar ke pemanggil.
    parsed_document = extract_document(document.file.path)
    extract_ms = _ms_since(started)

    def jalur_a():
        t = time.monotonic()
        result = run_jalur_a(
            document.file.path, rules=physical_rules, parsed_document=parsed_document,
        )
        return result, _ms_since(t)

    def jalur_b():
        t = time.monotonic()
        try:
            result = run_jalur_b(
                parsed_document,
                document_type=document_type_label,
                aspects=aspects,
            )
        except Exception as exc:  # pragma: no cover - pengaman tambahan
            logger.exception("Jalur B gagal. Document ID: %s", document.id)
            result = {
                "raw_response": "",
                "findings": [],
                "summary": {"passed": 0, "failed": 0, "total": 0},
                "error": str(exc),
                "error_type": "other",
                "model": "",
                "duration_ms": None,
                "unknown_categories": [],
            }
        return result, _ms_since(t)

    # 2. Pemrosesan paralel (Laporan Perancangan D.3): Jalur A (format,
    #    rule-based) dan Jalur B (AI Gemini) berjalan bersamaan.
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="jalur") as pool:
        future_a = pool.submit(jalur_a)
        future_b = pool.submit(jalur_b)
        jalur_a_result, jalur_a_ms = future_a.result()
        jalur_b_result, jalur_b_ms = future_b.result()

    timing = {
        "extract_ms": extract_ms,
        "jalur_a_ms": jalur_a_ms,
        "jalur_b_ms": jalur_b_ms,
        "total_ms": _ms_since(started),
    }

    # 3. Gabungkan temuan dan hitung skor.
    findings_a = jalur_a_result.get("findings", [])
    findings_b = jalur_b_result.get("findings", [])
    summary = {
        "physical": jalur_a_result.get("summary", {}),
        "semantic": jalur_b_result.get("summary", {}),
        "total_findings": len(findings_a) + len(findings_b),
    }
    result = build_result(jalur_a_result, jalur_b_result)

    # 4. Simpan hasil. Analisis ulang = temuan baru, jadi tanda "keliru"
    #    dan tinjauan sebelumnya direset (riwayatnya tetap ada di
    #    FindingFeedback untuk pengamatan pola).
    document.metadata = {
        **(document.metadata or {}),
        "jalur_a": jalur_a_result,
        "jalur_b": jalur_b_result,
        "summary": summary,
        # Waktu proses per tahap (ms), untuk metrik response time.
        "timing": timing,
    }
    AuditResult.objects.update_or_create(
        document=document,
        defaults={
            "physical_score": result["format_score"],
            "semantic_score": result["semantic_score"],
            "final_score": result["total_score"],
            "findings": result["findings"],
            "recommendations": {
                "has_format_score": result["has_format_score"],
                "has_semantic_score": result["has_semantic_score"],
                # True = dokumen lebih panjang dari batas, sebagian tidak dibaca AI.
                "text_truncated": bool(jalur_b_result.get("text_truncated")),
            },
            "rejected_findings": [],
            "corrected_score": None,
            "review_status": AuditResult.ReviewStatus.PENDING,
            "reviewed_by": None,
            "reviewed_at": None,
        },
    )
    document.status = "completed"
    document.save(update_fields=["metadata", "status", "updated_at"])

    # 5. Catat analisis AI untuk halaman "Kinerja AI".
    error = jalur_b_result.get("error")
    ai_run = AIRun.objects.create(
        document=document,
        trigger=trigger,
        triggered_by=user,
        status=AIRun.Status.FAILED if error else AIRun.Status.SUCCESS,
        error_type=jalur_b_result.get("error_type", "other") if error else "",
        error_message=(error or "")[:2000],
        model=jalur_b_result.get("model", ""),
        duration_ms=jalur_b_result.get("duration_ms"),
        rule_version=rule_version,
        findings=[f for f in result["findings"] if f.get("source") == "semantic"],
        unknown_categories=jalur_b_result.get("unknown_categories", []),
    )

    return {
        "jalur_a": jalur_a_result,
        "jalur_b": jalur_b_result,
        "result": result,
        "findings": findings_a + findings_b,
        "summary": summary,
        "ai_run": ai_run,
        "timing": timing,
    }
