from django.conf import settings
from django.db import models


class AuditResult(models.Model):

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Menunggu review"
        VALIDATED = "validated", "Tervalidasi"
        CORRECTED = "corrected", "Dikoreksi"

    document = models.OneToOneField(
        "documents.Document",
        on_delete=models.CASCADE,
        related_name="audit_result",
    )

    physical_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    semantic_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    final_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    findings = models.JSONField(
        default=list,
        blank=True,
    )

    recommendations = models.JSONField(
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # ---------- Review oleh admin (Web Dashboard) ----------

    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_audits",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    review_note = models.TextField(
        blank=True,
        default="",
    )

    # Skor akhir hasil koreksi admin. Kosong = pakai skor dari sistem.
    corrected_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Indeks temuan (pada field findings) yang dinilai keliru oleh admin.
    rejected_findings = models.JSONField(
        default=list,
        blank=True,
    )

    @property
    def effective_score(self):
        """Skor yang dipakai: hasil koreksi admin jika ada, selain itu skor sistem."""
        if self.corrected_score is not None:
            return self.corrected_score
        return self.final_score

    def __str__(self):
        return f"Audit Result - {self.document.title}"
