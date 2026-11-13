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


class AIRun(models.Model):
    """
    Catatan setiap analisis AI (Jalur B): saat upload atau saat admin
    menjalankan "Analisis ulang". Dipakai halaman "Kinerja AI" untuk
    mengamati keberhasilan, penyebab gagal, dan pola kesalahan AI.
    """

    class Status(models.TextChoices):
        SUCCESS = "success", "Berhasil"
        FAILED = "failed", "Gagal"

    class Trigger(models.TextChoices):
        UPLOAD = "upload", "Upload mahasiswa"
        REANALYZE = "reanalyze", "Analisis ulang admin"

    document = models.ForeignKey(
        "documents.Document",
        on_delete=models.CASCADE,
        related_name="ai_runs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    trigger = models.CharField(max_length=20, choices=Trigger.choices)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_runs",
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    # Kunci ERROR_LABELS di jalur_b_service (kosong jika berhasil).
    error_type = models.CharField(max_length=30, blank=True, default="")
    error_message = models.TextField(blank=True, default="")
    model = models.CharField(max_length=60, blank=True, default="")
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    # Versi aturan (RuleVersion) yang berlaku saat analisis.
    rule_version = models.PositiveIntegerField(default=0)
    # Temuan semantik hasil analisis ini (sudah dinormalisasi).
    findings = models.JSONField(default=list, blank=True)
    # Kategori dari AI yang tidak dikenali sistem.
    unknown_categories = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AI run #{self.pk} - {self.document_id} ({self.status})"


class FindingFeedback(models.Model):
    """
    Temuan yang ditandai keliru oleh admin. Disimpan terpisah dari
    AuditResult agar tetap ada walaupun dokumen dianalisis ulang,
    sehingga pola kesalahan AI bisa diamati dari waktu ke waktu.
    """

    document = models.ForeignKey(
        "documents.Document",
        on_delete=models.CASCADE,
        related_name="finding_feedback",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="finding_feedback",
    )
    source = models.CharField(max_length=20)       # physical / semantic
    aspect = models.CharField(max_length=60)       # rule_key / kategori
    title = models.CharField(max_length=255, blank=True, default="")
    detail = models.TextField(blank=True, default="")
    rule_version = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback {self.source}:{self.aspect} (doc {self.document_id})"
