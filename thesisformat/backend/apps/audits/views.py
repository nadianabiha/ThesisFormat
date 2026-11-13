"""
Endpoint Web Dashboard (khusus admin / staf).

    GET   /api/v1/admin/stats/                  statistik untuk halaman Ringkasan
    GET   /api/v1/admin/documents/              daftar dokumen (filter + halaman)
    GET   /api/v1/admin/documents/<id>/         detail dokumen + seluruh temuan
    PATCH /api/v1/admin/documents/<id>/review/  validasi / koreksi hasil AI

Sesuai arsitektur: dashboard hanya menampilkan dan memodifikasi data,
tidak menambah data baru (input hanya dari aplikasi mobile).
"""

from collections import Counter
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import F, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import Document
from apps.documents.serializers import get_document_result

from .models import AuditResult

User = get_user_model()

# Skor minimal agar dokumen dianggap "memenuhi standar" (sama dengan
# label "Good" di aplikasi mobile).
PASSING_SCORE = 75

SCORE_BUCKETS = [
    ("0-49", 0, 49),
    ("50-74", 50, 74),
    ("75-89", 75, 89),
    ("90-100", 90, 100),
]


def _student(user):
    return {
        "id": user.pk,
        "name": user.get_full_name().strip() or user.username,
        "email": user.email,
    }


def _document_summary(document):
    """Ringkasan satu dokumen untuk tabel dashboard."""
    result = get_document_result(document)
    audit = getattr(document, "audit_result", None)

    failed = 0
    if result:
        failed = sum(1 for f in result["findings"] if f.get("status") == "failed")

    return {
        "id": document.pk,
        "title": document.title,
        "document_type": document.document_type,
        "document_type_label": document.get_document_type_display(),
        "status": document.status,
        "uploaded_at": document.uploaded_at,
        "student": _student(document.user),
        "has_result": result is not None,
        "score": result["total_score"] if result else None,
        "format_score": result["format_score"] if result else None,
        "semantic_score": result["semantic_score"] if result else None,
        "has_semantic_score": bool(result and result["has_semantic_score"]),
        "failed_findings": failed,
        "review_status": audit.review_status if audit else None,
    }


def _document_detail(document, request):
    summary = _document_summary(document)
    audit = getattr(document, "audit_result", None)
    jalur_b = (document.metadata or {}).get("jalur_b") or {}

    findings = []
    if audit is not None:
        rejected = set(audit.rejected_findings or [])
        for index, finding in enumerate(audit.findings or []):
            findings.append({**finding, "index": index, "rejected": index in rejected})
    elif summary["has_result"]:
        # Dokumen lama tanpa AuditResult: hanya bisa dilihat, tidak bisa direview.
        result = get_document_result(document)
        for index, finding in enumerate(result["findings"]):
            findings.append({**finding, "index": index, "rejected": False})

    return {
        **summary,
        "file_url": request.build_absolute_uri(document.file.url) if document.file else None,
        "ai_error": jalur_b.get("error"),
        "findings": findings,
        "can_review": audit is not None,
        "review": None if audit is None else {
            "status": audit.review_status,
            "system_score": round(float(audit.final_score)),
            "corrected_score": (
                None if audit.corrected_score is None
                else round(float(audit.corrected_score))
            ),
            "note": audit.review_note,
            "reviewed_by": _student(audit.reviewed_by) if audit.reviewed_by else None,
            "reviewed_at": audit.reviewed_at,
        },
    }


def _base_queryset():
    return Document.objects.select_related(
        "user",
        "audit_result",
        "audit_result__reviewed_by",
    )


class AdminStatsView(APIView):
    """Statistik untuk halaman Ringkasan dashboard."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            weeks = min(max(int(request.query_params.get("weeks", 8)), 1), 52)
        except ValueError:
            weeks = 8

        documents = list(_base_queryset())
        now = timezone.localtime()
        week_ago = now - timedelta(days=7)

        scored = []          # (document, result) yang punya hasil pemeriksaan
        for document in documents:
            result = get_document_result(document)
            if result is not None:
                scored.append((document, result))

        scores = [result["total_score"] for _, result in scored]
        passing = sum(1 for s in scores if s >= PASSING_SCORE)
        ai_ok = sum(1 for _, result in scored if result["has_semantic_score"])

        review_counts = Counter(
            AuditResult.objects.values_list("review_status", flat=True)
        )

        overview = {
            "total_documents": len(documents),
            "total_students": User.objects.filter(is_staff=False).count(),
            "documents_this_week": sum(
                1 for d in documents if d.uploaded_at >= week_ago
            ),
            "average_score": round(sum(scores) / len(scores), 1) if scores else None,
            "passing_score": PASSING_SCORE,
            "passing_count": passing,
            "passing_rate": round(passing / len(scores) * 100, 1) if scores else None,
            "needs_improvement": len(scores) - passing,
            "ai_success_rate": round(ai_ok / len(scored) * 100, 1) if scored else None,
            "review": {
                key: review_counts.get(key, 0)
                for key in AuditResult.ReviewStatus.values
            },
        }

        # Rata-rata skor per jenis dokumen.
        score_by_type = []
        for value, label in Document.DocumentType.choices:
            type_scores = [
                result["total_score"]
                for document, result in scored
                if document.document_type == value
            ]
            score_by_type.append({
                "document_type": value,
                "label": label,
                "count": sum(1 for d in documents if d.document_type == value),
                "average_score": (
                    round(sum(type_scores) / len(type_scores), 1)
                    if type_scores else None
                ),
            })

        # Sebaran skor.
        score_distribution = [
            {
                "label": label,
                "count": sum(1 for s in scores if low <= s <= high),
            }
            for label, low, high in SCORE_BUCKETS
        ]

        # Tren mingguan (minggu dimulai hari Senin).
        this_monday = (now - timedelta(days=now.weekday())).date()
        trend = []
        for offset in range(weeks - 1, -1, -1):
            start = this_monday - timedelta(weeks=offset)
            end = start + timedelta(days=7)
            week_docs = [
                (document, result)
                for document, result in scored
                if start <= timezone.localtime(document.uploaded_at).date() < end
            ]
            uploads = sum(
                1 for d in documents
                if start <= timezone.localtime(d.uploaded_at).date() < end
            )
            week_scores = [result["total_score"] for _, result in week_docs]
            trend.append({
                "week_start": start.isoformat(),
                "uploads": uploads,
                "average_score": (
                    round(sum(week_scores) / len(week_scores), 1)
                    if week_scores else None
                ),
            })

        # Pelanggaran yang paling sering muncul (temuan "failed").
        finding_counter = Counter()
        for _, result in scored:
            for finding in result["findings"]:
                if finding.get("status") == "failed":
                    key = (finding.get("source", ""), finding.get("title", "Temuan"))
                    finding_counter[key] += 1

        top_findings = [
            {"source": source, "title": title, "count": count}
            for (source, title), count in finding_counter.most_common(8)
        ]

        return Response({
            "overview": overview,
            "score_by_type": score_by_type,
            "score_distribution": score_distribution,
            "trend": trend,
            "top_findings": top_findings,
        })


class AdminDocumentListView(APIView):
    """Daftar semua dokumen dengan filter, urutan, dan halaman."""

    permission_classes = [IsAdminUser]

    ORDERING = {
        "newest": ("-uploaded_at",),
        "oldest": ("uploaded_at",),
        "score_high": ("-effective_score", "-uploaded_at"),
        "score_low": ("effective_score", "-uploaded_at"),
    }

    def get(self, request):
        params = request.query_params
        queryset = _base_queryset().annotate(
            effective_score=Coalesce(
                "audit_result__corrected_score",
                "audit_result__final_score",
            ),
        )

        search = params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(user__email__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
            )

        if params.get("document_type"):
            queryset = queryset.filter(document_type=params["document_type"])

        if params.get("status"):
            queryset = queryset.filter(status=params["status"])

        review_status = params.get("review_status")
        if review_status == "none":
            queryset = queryset.filter(audit_result__isnull=True)
        elif review_status:
            queryset = queryset.filter(audit_result__review_status=review_status)

        ordering = self.ORDERING.get(params.get("ordering"), self.ORDERING["newest"])
        if ordering[0].lstrip("-") == "effective_score":
            # Dokumen tanpa skor selalu di bagian bawah.
            score = F("effective_score")
            first = (
                score.desc(nulls_last=True)
                if ordering[0].startswith("-")
                else score.asc(nulls_last=True)
            )
            queryset = queryset.order_by(first, *ordering[1:])
        else:
            queryset = queryset.order_by(*ordering)

        try:
            page_size = min(max(int(params.get("page_size", 10)), 1), 100)
            page = max(int(params.get("page", 1)), 1)
        except ValueError:
            page_size, page = 10, 1

        total = queryset.count()
        total_pages = max((total + page_size - 1) // page_size, 1)
        page = min(page, total_pages)
        start = (page - 1) * page_size
        items = [_document_summary(d) for d in queryset[start:start + page_size]]

        return Response({
            "results": items,
            "count": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        })


class AdminDocumentDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        document = _base_queryset().filter(pk=pk).first()
        if document is None:
            return Response(
                {"detail": "Dokumen tidak ditemukan."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(_document_detail(document, request))


class ReviewSerializer(serializers.Serializer):
    review_status = serializers.ChoiceField(choices=AuditResult.ReviewStatus.choices)
    corrected_score = serializers.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        allow_null=True,
    )
    review_note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )
    rejected_findings = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        required=False,
    )

    def validate(self, attrs):
        if (
            attrs["review_status"] == AuditResult.ReviewStatus.CORRECTED
            and attrs.get("corrected_score") is None
        ):
            raise serializers.ValidationError(
                {"corrected_score": "Skor koreksi wajib diisi jika status 'Dikoreksi'."}
            )

        total = self.context["findings_count"]
        rejected = attrs.get("rejected_findings")
        if rejected is not None:
            invalid = [i for i in rejected if i >= total]
            if invalid:
                raise serializers.ValidationError(
                    {"rejected_findings": f"Indeks temuan tidak valid: {invalid}."}
                )
            attrs["rejected_findings"] = sorted(set(rejected))
        return attrs


class AdminDocumentReviewView(APIView):
    """Validasi / koreksi hasil pemeriksaan AI oleh admin."""

    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        document = _base_queryset().filter(pk=pk).first()
        if document is None:
            return Response(
                {"detail": "Dokumen tidak ditemukan."},
                status=status.HTTP_404_NOT_FOUND,
            )

        audit = getattr(document, "audit_result", None)
        if audit is None:
            return Response(
                {"detail": "Dokumen ini belum memiliki hasil pemeriksaan yang bisa direview."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = ReviewSerializer(
            data=request.data,
            context={"findings_count": len(audit.findings or [])},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        audit.review_status = data["review_status"]

        if audit.review_status == AuditResult.ReviewStatus.CORRECTED:
            audit.corrected_score = data["corrected_score"]
        else:
            audit.corrected_score = None

        if "review_note" in data:
            audit.review_note = data["review_note"].strip()

        if "rejected_findings" in data:
            audit.rejected_findings = data["rejected_findings"]

        if audit.review_status == AuditResult.ReviewStatus.PENDING:
            audit.reviewed_by = None
            audit.reviewed_at = None
        else:
            audit.reviewed_by = request.user
            audit.reviewed_at = timezone.now()

        audit.save()

        document = _base_queryset().get(pk=pk)
        return Response(_document_detail(document, request))
