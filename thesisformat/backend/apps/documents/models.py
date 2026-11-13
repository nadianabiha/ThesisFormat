from django.conf import settings
from django.db import models


class Document(models.Model):

    class DocumentType(models.TextChoices):
        # Sesuai Panduan Penulisan Karya Ilmiah Polinela.
        # Nilai harus sama dengan lib/models/document_type.dart di Flutter.
        PRAKTIK = "praktik", "Laporan Praktik"
        PKL = "pkl", "Laporan PKL/Magang"
        TUGAS_AKHIR = "tugas_akhir", "Laporan Tugas Akhir/Skripsi"
        PROPOSAL_PENGABDIAN = "proposal_pengabdian", "Proposal Pengabdian Masyarakat"
        PROPOSAL_PENELITIAN = "proposal_penelitian", "Proposal Penelitian"
        MAKALAH_ILMIAH = "makalah_ilmiah", "Makalah Ilmiah"

    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    title = models.CharField(max_length=255)

    file = models.FileField(
        upload_to="documents/"
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.UPLOADED,
    )

    extracted_text = models.TextField(
        blank=True,
        null=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title