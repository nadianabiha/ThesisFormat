"""
Alur pemeriksaan dokumen: Jalur A (fisik) + Jalur B (AI) -> skor.

Dipakai oleh upload mahasiswa (DocumentUploadView) dan "Analisis ulang"
admin (Web Dashboard), sehingga keduanya memakai aturan & instruksi AI
yang sama, dan setiap analisis AI tercatat di AIRun.
"""

import logging

from apps.audits.models import AIRun, AuditResult
from apps.rules.models import MasterRule, RuleVersion

from .parser.jalur_a_service import run_jalur_a
from .scoring import build_result
from .semantic.jalur_b_service import run_jalur_b

logger = logging.getLogger(__name__)


def check_document(document, trigger=AIRun.Trigger.UPLOAD, user=None):
    """
    Jalankan pemeriksaan lengkap lalu simpan hasilnya.
    Mengembalikan dict: jalur_a, jalur_b, result, findings, summary, ai_run.
    Error Jalur A (mis. file tidak terbaca) dilempar ke pemanggil.
    """
    rule_version = RuleVersion.current()

    # 1. Jalur A: aturan fisik aktif sesuai jenis dokumen.
    physical_rules = MasterRule.for_document(
        MasterRule.Category.PHYSICAL,
        document.document_type,
    )
    jalur_a_result = run_jalur_a(document.file.path, rules=physical_rules)

    # 2. Jalur B: AI dengan instruksi per aspek dari MasterRule semantic.
    try:
        jalur_b_result = run_jalur_b(
            jalur_a_result["parsed_document"],
            document_type=document.get_document_type_display(),
            aspects=MasterRule.semantic_aspects(document.document_type),
        )
    except Exception as exc:  # pragma: no cover - pengaman tambahan
        logger.exception("Jalur B gagal. Document ID: %s", document.id)
        jalur_b_result = {
            "raw_response": "",
            "findings": [],
            "summary": {"passed": 0, "failed": 0, "total": 0},
            "error": str(exc),
            "error_type": "other",
            "model": "",
            "duration_ms": None,
            "unknown_categories": [],
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
    }
