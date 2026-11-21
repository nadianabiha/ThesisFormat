"""
Pengawasan & perbaikan kualitas AI oleh admin (Web Dashboard).

Siklus: AMATI pola kesalahan AI -> PERBAIKI aturan/instruksi AI ->
UJI ULANG pada dokumen yang dulu keliru -> bandingkan hasilnya.

    GET   /api/v1/admin/ai-performance/                    statistik kinerja AI
    GET   /api/v1/admin/ai-performance/retest-candidates/  dokumen untuk uji ulang
    POST  /api/v1/admin/documents/<id>/reanalyze/          analisis ulang 1 dokumen
    GET   /api/v1/admin/rules/                             aturan format & instruksi AI
    PATCH /api/v1/admin/rules/<id>/                        ubah aturan (tercatat sebagai versi)
"""

import os
from collections import Counter
from datetime import timedelta

from django.db.models import Avg, Count, Max, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import Document
from apps.documents.pipeline import check_document
from apps.documents.scoring import (
    PHYSICAL_LABELS,
    SEMANTIC_CATEGORIES,
    aspect_label,
    finding_aspect,
)
from apps.documents.semantic.jalur_b_service import ERROR_LABELS
from apps.documents.semantic.prompts import DEFAULT_ASPECTS
from apps.rules.models import MasterRule, RuleVersion

from .models import AIRun, AuditResult, FindingFeedback
from .views import _base_queryset, _document_detail, _document_summary


def _int_param(request, name, default, low, high):
    try:
        return min(max(int(request.query_params.get(name, default)), low), high)
    except (TypeError, ValueError):
        return default


def _rate(part, total):
    return round(part / total * 100, 1) if total else None


def _user_name(user):
    if user is None:
        return None
    return user.get_full_name().strip() or user.username


# ---------------------------------------------------------------------------
# 2. AMATI: Kinerja AI
# ---------------------------------------------------------------------------


class AIPerformanceView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        days = _int_param(request, "days", 30, 1, 365)
        now = timezone.now()
        since = now - timedelta(days=days)

        runs = AIRun.objects.filter(created_at__gte=since)
        total_runs = runs.count()
        success_runs = runs.filter(status=AIRun.Status.SUCCESS).count()
        avg_duration = runs.filter(
            status=AIRun.Status.SUCCESS, duration_ms__isnull=False,
        ).aggregate(value=Avg("duration_ms"))["value"]

        failure_reasons = [
            {
                "type": row["error_type"] or "other",
                "label": ERROR_LABELS.get(row["error_type"], ERROR_LABELS["other"]),
                "count": row["count"],
            }
            for row in runs.filter(status=AIRun.Status.FAILED)
            .values("error_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        ]
        by_model = [
            {"model": row["model"], "count": row["count"]}
            for row in runs.exclude(model="")
            .values("model")
            .annotate(count=Count("id"))
            .order_by("-count")
        ]

        unknown_counter = Counter()
        unknown_runs = 0
        for categories in runs.values_list("unknown_categories", flat=True):
            if categories:
                unknown_runs += 1
                unknown_counter.update(categories)

        # Tren mingguan keberhasilan analisis AI.
        today = timezone.localtime(now).date()
        weeks = max(1, min(12, (days + 6) // 7))
        this_monday = today - timedelta(days=today.weekday())
        week_rows = {
            this_monday - timedelta(weeks=offset): [0, 0]
            for offset in range(weeks - 1, -1, -1)
        }
        for created_at, run_status in runs.values_list("created_at", "status"):
            day = timezone.localtime(created_at).date()
            monday = day - timedelta(days=day.weekday())
            if monday in week_rows:
                week_rows[monday][0] += 1
                if run_status == AIRun.Status.SUCCESS:
                    week_rows[monday][1] += 1
        trend = [
            {
                "week_start": monday.isoformat(),
                "runs": total,
                "success": ok,
                "failed": total - ok,
                "success_rate": _rate(ok, total),
            }
            for monday, (total, ok) in week_rows.items()
        ]

        return Response({
            "period_days": days,
            "current_rule_version": RuleVersion.current(),
            "runs": {
                "total": total_runs,
                "success": success_runs,
                "failed": total_runs - success_runs,
                "success_rate": _rate(success_runs, total_runs),
                "avg_duration_ms": round(avg_duration) if avg_duration else None,
                "by_model": by_model,
                "failure_reasons": failure_reasons,
                "unknown_category_runs": unknown_runs,
                "unknown_categories": [
                    {"category": name, "count": count}
                    for name, count in unknown_counter.most_common(5)
                ],
            },
            "trend": trend,
            "recent_runs": self._recent_runs(runs),
            "aspects": self._aspects(since),
            "recent_feedback": self._recent_feedback(since),
            "versions": self._versions(),
            "feedback_total": FindingFeedback.objects.filter(created_at__gte=since).count(),
        })

    @staticmethod
    def _recent_runs(runs, limit=10):
        """Analisis AI terbaru: dokumen apa, berhasil/gagal, dan penyebabnya."""
        return [
            {
                "id": run.pk,
                "document_id": run.document_id,
                "document_title": run.document.title,
                "created_at": run.created_at,
                "status": run.status,
                "trigger": run.trigger,
                "error_label": ERROR_LABELS.get(run.error_type, "") if run.error_type else "",
                "model": run.model,
                "duration_ms": run.duration_ms,
            }
            for run in runs.select_related("document").order_by("-created_at")[:limit]
        ]

    @staticmethod
    def _aspects(since):
        """Pola kesalahan per aspek: temuan gagal dari sistem vs ditandai keliru."""
        failed = Counter()
        audits = AuditResult.objects.filter(document__uploaded_at__gte=since)
        for findings in audits.values_list("findings", flat=True):
            for finding in findings or []:
                if finding.get("status") == "failed":
                    failed[finding_aspect(finding)] += 1

        feedback = Counter(
            (row["source"], row["aspect"])
            for row in FindingFeedback.objects.filter(created_at__gte=since)
            .values("source", "aspect")
        )

        enabled = {
            ("semantic" if rule.category == MasterRule.Category.SEMANTIC else "physical", rule.rule_key): rule.active
            for rule in MasterRule.objects.filter(document_type="")
        }

        keys = {("semantic", key) for key in SEMANTIC_CATEGORIES}
        keys |= {("physical", key) for key in PHYSICAL_LABELS if ("physical", key) in enabled}
        keys |= set(failed) | set(feedback)

        rows = []
        for source, key in keys:
            failed_count = failed.get((source, key), 0)
            feedback_count = feedback.get((source, key), 0)
            rows.append({
                "source": source,
                "aspect": key,
                "label": aspect_label(source, key),
                "failed_count": failed_count,
                "feedback_count": feedback_count,
                "feedback_rate": _rate(feedback_count, failed_count),
                "enabled": enabled.get((source, key), True),
            })
        rows.sort(key=lambda r: (-r["feedback_count"], -(r["feedback_rate"] or 0), r["label"]))
        return rows

    @staticmethod
    def _recent_feedback(since):
        items = (
            FindingFeedback.objects.filter(created_at__gte=since)
            .select_related("document", "created_by")[:10]
        )
        return [
            {
                "id": fb.pk,
                "document_id": fb.document_id,
                "document_title": fb.document.title,
                "source": fb.source,
                "aspect": fb.aspect,
                "aspect_label": aspect_label(fb.source, fb.aspect),
                "detail": fb.detail,
                "created_by": _user_name(fb.created_by),
                "created_at": fb.created_at,
                "rule_version": fb.rule_version,
            }
            for fb in items
        ]

    @staticmethod
    def _versions():
        """Kinerja AI per versi aturan (untuk membandingkan sebelum/sesudah)."""
        run_stats = {
            row["rule_version"]: row
            for row in AIRun.objects.values("rule_version").annotate(
                total=Count("id"),
                success=Count("id", filter=Q(status=AIRun.Status.SUCCESS)),
            )
        }
        feedback_stats = Counter(
            FindingFeedback.objects.values_list("rule_version", flat=True)
        )
        failed_semantic = Counter()
        for version, findings in AIRun.objects.values_list("rule_version", "findings"):
            failed_semantic[version] += sum(
                1 for f in findings or [] if f.get("status") == "failed"
            )

        def row(number, created_at=None, created_by=None, note="", changes=0):
            stats = run_stats.get(number, {"total": 0, "success": 0})
            return {
                "version": number,
                "created_at": created_at,
                "created_by": created_by,
                "note": note,
                "changes": changes,
                "runs": stats["total"],
                "success_rate": _rate(stats["success"], stats["total"]),
                "feedback_count": feedback_stats.get(number, 0),
                "ai_failed_findings": failed_semantic.get(number, 0),
            }

        versions = [
            row(
                version.pk,
                version.created_at,
                _user_name(version.created_by),
                version.note,
                len(version.changes or []),
            )
            for version in RuleVersion.objects.select_related("created_by")[:10]
        ]
        versions.append(row(0, note="Aturan awal"))
        return versions


class RetestCandidatesView(APIView):
    """Dokumen yang pernah ditandai keliru pada suatu aspek (untuk uji ulang)."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        source = request.query_params.get("source", "")
        aspect = request.query_params.get("aspect", "")
        limit = _int_param(request, "limit", 5, 1, 20)

        feedback = FindingFeedback.objects.all()
        if source:
            feedback = feedback.filter(source=source)
        if aspect:
            feedback = feedback.filter(aspect=aspect)

        rows = (
            feedback.values("document_id")
            .annotate(feedback_count=Count("id"), last_feedback=Max("created_at"))
            .order_by("-last_feedback")
        )
        documents = Document.objects.in_bulk([row["document_id"] for row in rows])

        results = []
        for row in rows:
            document = documents.get(row["document_id"])
            if document is None or not document.file:
                continue
            results.append({
                "document_id": document.pk,
                "title": document.title,
                "feedback_count": row["feedback_count"],
                "last_feedback": row["last_feedback"],
            })
            if len(results) >= limit:
                break
        return Response({"results": results, "count": len(results)})


# ---------------------------------------------------------------------------
# 4. BUKTIKAN: analisis ulang + perbandingan sebelum/sesudah
# ---------------------------------------------------------------------------


class AdminDocumentReanalyzeView(APIView):
    """Jalankan ulang Jalur A + Jalur B dengan aturan & instruksi AI terbaru."""

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        document = _base_queryset().filter(pk=pk).first()
        if document is None:
            return Response(
                {"detail": "Dokumen tidak ditemukan."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not document.file or not os.path.exists(document.file.path):
            return Response(
                {"detail": "File dokumen tidak ditemukan di server, tidak bisa dianalisis ulang."},
                status=status.HTTP_409_CONFLICT,
            )

        before = _document_summary(document)
        feedback = list(document.finding_feedback.all())

        try:
            checked = check_document(
                document,
                trigger=AIRun.Trigger.REANALYZE,
                user=request.user,
            )
        except Exception as exc:
            return Response(
                {"detail": f"Analisis ulang gagal: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        document = _base_queryset().get(pk=pk)
        after = _document_summary(document)
        run = checked["ai_run"]

        # Apakah kesalahan yang dulu ditandai keliru masih muncul?
        failed_now = {
            finding_aspect(f)
            for f in (document.audit_result.findings or [])
            if f.get("status") == "failed"
        }
        seen = set()
        items = []
        for fb in feedback:
            key = (fb.source, fb.aspect)
            if key in seen:
                continue
            seen.add(key)
            ai_failed = fb.source == "semantic" and run.status == AIRun.Status.FAILED
            items.append({
                "source": fb.source,
                "aspect": fb.aspect,
                "label": aspect_label(fb.source, fb.aspect),
                "previous_detail": fb.detail,
                # None = tidak bisa dinilai karena analisis AI gagal.
                "still_present": None if ai_failed else key in failed_now,
            })

        return Response({
            "document": _document_detail(document, request),
            "comparison": {
                "before_score": before["score"],
                "after_score": after["score"],
                "ai_status": run.status,
                "ai_error": run.error_message or None,
                "ai_error_label": ERROR_LABELS.get(run.error_type, "") if run.error_type else "",
                "rule_version": run.rule_version,
                "feedback": items,
                "resolved": sum(1 for i in items if i["still_present"] is False),
                "still_present": sum(1 for i in items if i["still_present"] is True),
            },
        })


# ---------------------------------------------------------------------------
# 3. PERBAIKI: aturan format & instruksi AI (tercatat sebagai versi)
# ---------------------------------------------------------------------------

ALIGNMENTS = ["LEFT", "CENTER", "RIGHT", "JUSTIFY"]

PHYSICAL_INPUTS = {
    "font_name": {"type": "text"},
    "font_size": {"type": "number", "min": 6, "max": 30, "step": 0.5, "unit": "pt"},
    "alignment": {"type": "select", "options": ALIGNMENTS},
    "line_spacing": {"type": "number", "min": 1, "max": 3, "step": 0.05, "unit": "spasi"},
    "margin": {"type": "margin", "min": 0, "max": 10, "unit": "cm"},
    # Aturan tata letak (migration rules 0007): nilainya berisi beberapa
    # angka/pilihan sekaligus, jadi butuh kolom isian khusus.
    "paper_size": {"type": "size", "min": 1, "max": 60, "unit": "cm"},
    "logo_size": {"type": "size", "min": 0.1, "max": 30, "unit": "cm"},
    "page_number": {
        "type": "page_number",
        "formats": ["roman_lower", "roman_upper", "arabic"],
        "verticals": ["top", "bottom"],
        "horizontals": ["left", "center", "right"],
    },
    "cover": {"type": "cover", "elements": ["logo", "npm", "institusi", "tahun"]},
}

MARGIN_KEYS = ["top_margin", "right_margin", "bottom_margin", "left_margin"]
SIZE_KEYS = ["width_cm", "height_cm", "tolerance_cm"]
PAGE_GROUPS = ["front", "body"]


def _rule_snapshot(rule):
    value = rule.rule_value if isinstance(rule.rule_value, dict) else {"value": rule.rule_value}
    if rule.category == MasterRule.Category.SEMANTIC:
        return {"instruction": value.get("instruction", ""), "active": rule.active}
    return {"value": value.get("value"), "active": rule.active}


def _serialize_rule(rule):
    value = rule.rule_value if isinstance(rule.rule_value, dict) else {"value": rule.rule_value}
    base = {
        "id": rule.pk,
        "rule_key": rule.rule_key,
        "category": rule.category,
        "document_type": rule.document_type,
        "document_type_label": (
            rule.get_document_type_display() if rule.document_type else "Semua jenis dokumen"
        ),
        "active": rule.active,
        "updated_at": rule.updated_at,
    }
    if rule.category == MasterRule.Category.SEMANTIC:
        default = next((a for a in DEFAULT_ASPECTS if a["key"] == rule.rule_key), {})
        return {
            **base,
            "label": value.get("label") or default.get("label") or rule.rule_key,
            "instruction": value.get("instruction", ""),
            "default_instruction": default.get("instruction", ""),
        }
    return {
        **base,
        "label": PHYSICAL_LABELS.get(rule.rule_key, rule.rule_key),
        "value": value.get("value"),
        "input": PHYSICAL_INPUTS.get(rule.rule_key, {"type": "text"}),
    }


def _clean_physical_value(rule_key, value):
    """Validasi nilai aturan fisik. Mengembalikan (nilai, pesan_error)."""
    spec = PHYSICAL_INPUTS.get(rule_key, {"type": "text"})
    kind = spec["type"]

    if kind == "text":
        text = str(value or "").strip()
        if not text or len(text) > 100:
            return None, "Isi nama (1-100 karakter)."
        return text, None

    if kind == "select":
        text = str(value or "").strip().upper()
        if text not in spec["options"]:
            return None, f"Pilih salah satu: {', '.join(spec['options'])}."
        return text, None

    if kind == "number":
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None, "Isi dengan angka."
        if not spec["min"] <= number <= spec["max"]:
            return None, f"Nilai harus antara {spec['min']} dan {spec['max']}."
        return (int(number) if number.is_integer() else number), None

    if kind == "margin":
        if not isinstance(value, dict):
            return None, "Isi keempat margin (atas, kanan, bawah, kiri)."
        cleaned = {}
        for key in MARGIN_KEYS:
            try:
                number = float(value.get(key))
            except (TypeError, ValueError):
                return None, "Isi keempat margin dengan angka."
            if not spec["min"] <= number <= spec["max"]:
                return None, f"Margin harus antara {spec['min']} dan {spec['max']} cm."
            cleaned[key] = int(number) if number.is_integer() else number
        return cleaned, None

    if kind == "size":
        if not isinstance(value, dict):
            return None, "Isi lebar, tinggi, dan toleransi."
        cleaned = {}
        for key in SIZE_KEYS:
            try:
                number = float(value.get(key))
            except (TypeError, ValueError):
                return None, "Isi lebar, tinggi, dan toleransi dengan angka."
            low = 0 if key == "tolerance_cm" else spec["min"]
            high = 5 if key == "tolerance_cm" else spec["max"]
            if not low <= number <= high:
                return None, f"Nilai harus antara {low} dan {high} cm."
            cleaned[key] = int(number) if number.is_integer() else number
        return cleaned, None

    if kind == "page_number":
        if not isinstance(value, dict):
            return None, "Isi aturan nomor halaman awal dan bagian isi."
        cleaned = {}
        for group in PAGE_GROUPS:
            part = value.get(group)
            if not isinstance(part, dict):
                return None, "Isi aturan nomor halaman awal dan bagian isi."
            # Letak boleh "Tidak dicek" (kosong/None): pedoman Polinela tidak
            # menjelaskan letaknya dengan tegas, jadi admin boleh tidak menilainya.
            fmt = part.get("format")
            vertical = part.get("vertical") or None
            horizontal = part.get("horizontal") or None
            if fmt not in spec["formats"] \
                    or (vertical is not None and vertical not in spec["verticals"]) \
                    or (horizontal is not None and horizontal not in spec["horizontals"]):
                return None, "Pilih format, letak, dan posisi nomor halaman."
            cleaned[group] = {"format": fmt, "vertical": vertical, "horizontal": horizontal}
        return cleaned, None

    if kind == "cover":
        if not isinstance(value, dict):
            return None, "Pilih elemen sampul yang wajib."
        required = [key for key in spec["elements"] if key in (value.get("required") or [])]
        if not required:
            return None, "Pilih minimal satu elemen sampul yang wajib."
        institution = str(value.get("institution") or "").strip()
        if "institusi" in required and not 1 <= len(institution) <= 100:
            return None, "Isi nama institusi (1-100 karakter)."
        return {"required": required, "institution": institution or "POLITEKNIK NEGERI LAMPUNG"}, None

    return value, None


class RuleListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        rules = MasterRule.objects.all().order_by("document_type", "rule_key")
        order = {a["key"]: i for i, a in enumerate(DEFAULT_ASPECTS)}

        physical = [_serialize_rule(r) for r in rules if r.category == MasterRule.Category.PHYSICAL]
        semantic = sorted(
            (_serialize_rule(r) for r in rules if r.category == MasterRule.Category.SEMANTIC),
            key=lambda r: (r["document_type"], order.get(r["rule_key"], 99)),
        )
        return Response({
            "current_version": RuleVersion.current(),
            "physical": physical,
            "semantic": semantic,
        })


class RuleDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        rule = MasterRule.objects.filter(pk=pk).first()
        if rule is None:
            return Response({"detail": "Aturan tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        before = _rule_snapshot(rule)
        value = dict(rule.rule_value) if isinstance(rule.rule_value, dict) else {"value": rule.rule_value}
        errors = {}

        if "active" in data:
            if not isinstance(data["active"], bool):
                errors["active"] = "Isi true atau false."
            else:
                rule.active = data["active"]

        if rule.category == MasterRule.Category.SEMANTIC:
            if "instruction" in data:
                instruction = str(data["instruction"] or "").strip()
                if not instruction:
                    errors["instruction"] = "Instruksi AI tidak boleh kosong."
                elif len(instruction) > 3000:
                    errors["instruction"] = "Instruksi AI maksimal 3000 karakter."
                else:
                    value["instruction"] = instruction
        elif "value" in data:
            cleaned, error = _clean_physical_value(rule.rule_key, data["value"])
            if error:
                errors["value"] = error
            else:
                value["value"] = cleaned

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        rule.rule_value = value
        after = _rule_snapshot(rule)
        if after == before:
            return Response(
                {"detail": "Tidak ada perubahan pada aturan ini."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Minimal satu aspek AI harus tetap aktif agar Jalur B bisa berjalan.
        if rule.category == MasterRule.Category.SEMANTIC and not rule.active:
            other_active = MasterRule.objects.filter(
                category=MasterRule.Category.SEMANTIC,
                document_type=rule.document_type,
                active=True,
            ).exclude(pk=rule.pk).exists()
            if not other_active:
                return Response(
                    {"active": "Minimal satu aspek AI harus tetap aktif."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        rule.save()

        label = _serialize_rule(rule)["label"]
        kind = "instruksi AI" if rule.category == MasterRule.Category.SEMANTIC else "aturan format"
        note = str(data.get("note") or "").strip()[:255] or f"Ubah {kind}: {label}"
        version = RuleVersion.objects.create(
            created_by=request.user,
            note=note,
            changes=[{
                "rule_id": rule.pk,
                "rule_key": rule.rule_key,
                "category": rule.category,
                "document_type": rule.document_type,
                "before": before,
                "after": after,
            }],
        )

        return Response({"rule": _serialize_rule(rule), "version": version.pk})
