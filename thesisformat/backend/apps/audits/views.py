"""
Endpoint Web Dashboard (khusus admin / staf).

    GET   /api/v1/admin/stats/                  statistik untuk halaman Ringkasan
    GET   /api/v1/admin/documents/              daftar dokumen (filter + halaman)
    GET   /api/v1/admin/students/               daftar mahasiswa + ringkasan dokumen
    GET   /api/v1/admin/documents/<id>/         detail dokumen + seluruh temuan
    PATCH /api/v1/admin/documents/<id>/review/  tandai temuan keliru + catatan

Endpoint pengawasan kualitas AI ada di ai_views.py.

Sesuai arsitektur: dashboard hanya menampilkan dan memodifikasi data,
tidak menambah data baru (input hanya dari aplikasi mobile).
"""

from collections import Counter
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, F, Max, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import Document
from apps.documents.scoring import aspect_label, finding_aspect, scores_from_findings
from apps.documents.semantic.jalur_b_service import ERROR_LABELS
from apps.documents.serializers import get_document_result
from apps.rules.models import RuleVersion

from .models import AuditResult, FindingFeedback

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


def _with_aspect(finding, index, rejected):
    source, key = finding_aspect(finding)
    return {
        **finding,
        "index": index,
        "rejected": rejected,
        "aspect": key,
        "aspect_label": aspect_label(source, key),
    }


def _ai_run_info(run):
    if run is None:
        return None
    return {
        "id": run.pk,
        "status": run.status,
        "trigger": run.trigger,
        "error_type": run.error_type,
        "error_label": ERROR_LABELS.get(run.error_type, ""),
        "model": run.model,
        "duration_ms": run.duration_ms,
        "rule_version": run.rule_version,
        "created_at": run.created_at,
        "unknown_categories": run.unknown_categories,
    }


def _document_detail(document, request):
    summary = _document_summary(document)
    audit = getattr(document, "audit_result", None)
    jalur_b = (document.metadata or {}).get("jalur_b") or {}

    findings = []
    if audit is not None:
        rejected = set(audit.rejected_findings or [])
        for index, finding in enumerate(audit.findings or []):
            findings.append(_with_aspect(finding, index, index in rejected))
    elif summary["has_result"]:
        # Dokumen lama tanpa AuditResult: hanya bisa dilihat, tidak bisa ditinjau.
        result = get_document_result(document)
        for index, finding in enumerate(result["findings"]):
            findings.append(_with_aspect(finding, index, False))

    runs = list(document.ai_runs.all()[:5])

    return {
        **summary,
        "file_url": request.build_absolute_uri(document.file.url) if document.file else None,
        "ai_error": jalur_b.get("error"),
        "findings": findings,
        "can_review": audit is not None,
        "can_reanalyze": bool(document.file),
        "ai": _ai_run_info(runs[0] if runs else None),
        "ai_runs": [_ai_run_info(run) for run in runs],
        "review": None if audit is None else {
            "status": audit.review_status,
            # Skor dari sistem sebelum ada temuan yang ditandai keliru.
            "system_score": round(float(audit.final_score)),
            # Skor hasil hitung ulang otomatis (None jika tidak ada temuan keliru).
            "corrected_score": (
                None if audit.corrected_score is None
                else round(float(audit.corrected_score))
            ),
            "removed_findings": len(audit.rejected_findings or []),
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

        # (document, result) yang punya hasil pemeriksaan tersimpan (AuditResult).
        # Dokumen lama tanpa AuditResult tidak dihitung agar angka statistik
        # sama dengan hasil filter di halaman Dokumen (filter skor & AI
        # memakai AuditResult) dan semua dokumen yang dihitung bisa direview.
        scored = []
        for document in documents:
            if getattr(document, "audit_result", None) is None:
                continue
            result = get_document_result(document)
            if result is not None:
                scored.append((document, result))

        # Nilai hanya dihitung dari hasil LENGKAP (format + isi). Jika AI gagal,
        # nilai yang tersimpan hanya nilai format, jadi tidak ikut dirata-rata.
        complete = [(d, r) for d, r in scored if r["has_semantic_score"]]
        scores = [result["total_score"] for _, result in complete]
        passing = sum(1 for s in scores if s >= PASSING_SCORE)
        ai_ok = len(complete)

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
            # Dokumen yang pemeriksaan isinya (AI) gagal: belum punya nilai akhir.
            "incomplete_count": len(scored) - len(complete),
            "ai_success_rate": round(ai_ok / len(scored) * 100, 1) if scored else None,
            "review": {
                key: review_counts.get(key, 0)
                for key in AuditResult.ReviewStatus.values
            },
            # Jumlah temuan yang ditandai keliru (umpan balik perbaikan AI).
            "feedback_total": FindingFeedback.objects.count(),
        }

        # Rata-rata skor per jenis dokumen.
        score_by_type = []
        for value, label in Document.DocumentType.choices:
            type_scores = [
                result["total_score"]
                for document, result in complete
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
                for document, result in complete
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

        # Rentang skor (skor koreksi admin jika ada, selain itu skor sistem).
        # Hanya hasil lengkap: jika AI gagal, skor tersimpan hanya skor format.
        for param, lookup in (("score_min", "gte"), ("score_max", "lte")):
            value = params.get(param)
            if value not in (None, ""):
                try:
                    queryset = queryset.filter(
                        **{f"effective_score__{lookup}": int(value)},
                        audit_result__recommendations__has_semantic_score=True,
                    )
                except ValueError:
                    pass

        # Status analisis AI (Jalur B).
        ai = params.get("ai")
        if ai == "success":
            queryset = queryset.filter(
                audit_result__recommendations__has_semantic_score=True,
            )
        elif ai == "failed":
            queryset = queryset.filter(audit_result__isnull=False).exclude(
                audit_result__recommendations__has_semantic_score=True,
            )

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


class AdminStudentListView(APIView):
    """Daftar mahasiswa (akun non-staf) beserta ringkasan dokumennya."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = User.objects.filter(is_staff=False).annotate(
            document_count=Count("documents", distinct=True),
            last_upload=Max("documents__uploaded_at"),
            # Rata-rata hanya dari hasil lengkap (AI berhasil).
            average_score=Avg(
                Coalesce(
                    "documents__audit_result__corrected_score",
                    "documents__audit_result__final_score",
                ),
                filter=Q(documents__audit_result__recommendations__has_semantic_score=True),
            ),
            pending_review=Count(
                "documents__audit_result",
                filter=Q(documents__audit_result__review_status=AuditResult.ReviewStatus.PENDING),
                distinct=True,
            ),
        )

        search = request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(username__icontains=search)
            )

        queryset = queryset.order_by(F("last_upload").desc(nulls_last=True), "first_name")

        results = [
            {
                **_student(user),
                "date_joined": user.date_joined,
                "document_count": user.document_count,
                "last_upload": user.last_upload,
                "average_score": (
                    None if user.average_score is None
                    else round(float(user.average_score), 1)
                ),
                "pending_review": user.pending_review,
            }
            for user in queryset
        ]
        return Response({"results": results, "count": len(results)})


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


# ---------------------------------------------------------------------------
# Tinjauan admin: menandai temuan yang keliru.
# Admin TIDAK menilai sendiri; skor dihitung ulang otomatis oleh sistem, dan
# setiap tanda "keliru" disimpan sebagai umpan balik (FindingFeedback) untuk
# mengamati pola kesalahan AI di halaman "Kinerja AI".
# ---------------------------------------------------------------------------


class ReviewSerializer(serializers.Serializer):
    rejected_findings = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        required=False,
    )
    review_note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )

    def validate_rejected_findings(self, value):
        findings = self.context["findings"]
        invalid = [i for i in value if i >= len(findings)]
        if invalid:
            raise serializers.ValidationError(f"Indeks temuan tidak valid: {invalid}.")
        passed = [i for i in value if findings[i].get("status") == "passed"]
        if passed:
            raise serializers.ValidationError(
                "Temuan yang lulus tidak perlu ditandai keliru."
            )
        return sorted(set(value))


def _feedback_key(source, aspect, detail):
    return (source, aspect, (detail or "").strip())


def _sync_feedback(document, audit, user):
    """
    Samakan FindingFeedback dengan tanda "keliru" saat ini:
    - temuan yang baru ditandai -> buat umpan balik,
    - temuan yang tandanya dibatalkan -> hapus umpan baliknya.
    Umpan balik untuk temuan lama (sebelum analisis ulang) tidak disentuh.
    """
    rejected = set(audit.rejected_findings or [])
    current = {}
    for index, finding in enumerate(audit.findings or []):
        source, aspect = finding_aspect(finding)
        key = _feedback_key(source, aspect, finding.get("detail"))
        current[key] = (index in rejected, finding)

    existing = {
        _feedback_key(fb.source, fb.aspect, fb.detail): fb
        for fb in document.finding_feedback.all()
    }

    version = RuleVersion.current()
    for key, (is_rejected, finding) in current.items():
        if is_rejected and key not in existing:
            FindingFeedback.objects.create(
                document=document,
                created_by=user,
                source=key[0],
                aspect=key[1],
                title=str(finding.get("title", ""))[:255],
                detail=key[2],
                rule_version=version,
            )
        elif not is_rejected and key in existing:
            existing[key].delete()


class AdminDocumentReviewView(APIView):
    """Simpan tinjauan admin: tanda temuan keliru + catatan."""

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
                {"detail": "Dokumen ini belum memiliki hasil pemeriksaan yang bisa ditinjau."},
                status=status.HTTP_409_CONFLICT,
            )

        findings = audit.findings or []
        serializer = ReviewSerializer(
            data=request.data,
            context={"findings": findings},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if "rejected_findings" in data:
            audit.rejected_findings = data["rejected_findings"]
        if "review_note" in data:
            audit.review_note = data["review_note"].strip()

        rejected = set(audit.rejected_findings or [])
        if rejected:
            kept = [f for i, f in enumerate(findings) if i not in rejected]
            # Skor dihitung ulang otomatis dengan rumus yang sama (40/60).
            audit.corrected_score = scores_from_findings(kept)["total_score"]
            audit.review_status = AuditResult.ReviewStatus.CORRECTED
        else:
            audit.corrected_score = None
            audit.review_status = AuditResult.ReviewStatus.VALIDATED

        audit.reviewed_by = request.user
        audit.reviewed_at = timezone.now()
        audit.save()

        _sync_feedback(document, audit, request.user)

        document = _base_queryset().get(pk=pk)
        return Response(_document_detail(document, request))


