from rest_framework import serializers

from .models import Document
from .scoring import result_from_metadata


def get_document_result(document):
    """
    Ambil hasil pemeriksaan dokumen.
    1. Pakai AuditResult jika sudah tersimpan.
    2. Jika belum (dokumen lama), hitung dari metadata hasil upload.
    """
    audit = getattr(document, "audit_result", None)
    if audit is not None:
        stored = audit.recommendations if isinstance(audit.recommendations, dict) else {}
        # Temuan yang dinilai keliru oleh admin (Web Dashboard) tidak
        # ditampilkan ke mahasiswa, dan skor koreksi admin menggantikan
        # skor sistem.
        rejected = set(audit.rejected_findings or [])
        findings = [
            finding
            for index, finding in enumerate(audit.findings or [])
            if index not in rejected
        ]
        return {
            "total_score": round(float(audit.effective_score)),
            "format_score": round(float(audit.physical_score)),
            "semantic_score": round(float(audit.semantic_score)),
            "has_format_score": stored.get("has_format_score", True),
            "has_semantic_score": stored.get("has_semantic_score", False),
            "findings": findings,
            "review_status": audit.review_status,
            "review_note": audit.review_note,
        }
    return result_from_metadata(document.metadata)


class DocumentSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(source="title", read_only=True)
    upload_date = serializers.DateTimeField(source="uploaded_at", read_only=True)
    score = serializers.SerializerMethodField()
    findings_count = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "id",
            "title",
            "file",
            "document_type",
            "status",
            "uploaded_at",
            "updated_at",
            "file_name",
            "upload_date",
            "score",
            "findings_count",
            "result",
        )
        read_only_fields = (
            "id",
            "status",
            "uploaded_at",
            "updated_at",
        )

    def get_result(self, obj):
        return get_document_result(obj)

    def get_score(self, obj):
        result = get_document_result(obj)
        return result["total_score"] if result else 0

    def get_findings_count(self, obj):
        # Jumlah item yang perlu perhatian (bukan yang sudah lulus).
        result = get_document_result(obj)
        if not result:
            return 0
        return sum(1 for f in result["findings"] if f.get("status") != "passed")
