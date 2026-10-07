from django.db import models


class AuditResult(models.Model):

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

    def __str__(self):
        return f"Audit Result - {self.document.title}"