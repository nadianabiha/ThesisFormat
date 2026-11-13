from django.db import models

from apps.documents.models import Document


class MasterRule(models.Model):

    class Category(models.TextChoices):
        PHYSICAL = "physical", "Physical"
        SEMANTIC = "semantic", "Semantic"

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )

    # Kosong = aturan umum untuk semua jenis dokumen.
    # Diisi = aturan khusus jenis itu, dan menimpa aturan umum dengan rule_key sama.
    document_type = models.CharField(
        max_length=30,
        choices=Document.DocumentType.choices,
        blank=True,
        default="",
    )

    rule_key = models.CharField(
        max_length=100,
    )

    rule_value = models.JSONField(
        default=dict,
    )

    description = models.TextField(
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @classmethod
    def for_document(cls, category, document_type):
        """
        Aturan aktif untuk satu jenis dokumen: aturan umum ditambah aturan
        khusus. Jika rule_key sama, aturan khusus yang dipakai.
        """
        rules = cls.objects.filter(
            category=category,
            active=True,
            document_type__in=["", document_type],
        )
        by_key = {}
        for rule in rules:
            if rule.rule_key not in by_key or rule.document_type:
                by_key[rule.rule_key] = rule
        return list(by_key.values())

    def __str__(self):
        label = self.get_document_type_display() if self.document_type else "Umum"
        return f"{self.rule_key} ({label})"