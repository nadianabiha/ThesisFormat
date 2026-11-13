from django.conf import settings
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

    @classmethod
    def semantic_aspects(cls, document_type):
        """
        Aspek pemeriksaan AI (Jalur B) yang aktif untuk satu jenis dokumen,
        dalam urutan baku: [{"key", "label", "instruction"}].

        rule_value aturan semantik: {"label": ..., "instruction": ...}.
        Mengembalikan None jika belum ada aturan semantik sama sekali
        (Jalur B lalu memakai instruksi bawaan di prompts.py).
        """
        from apps.documents.semantic.prompts import DEFAULT_ASPECTS

        if not cls.objects.filter(category=cls.Category.SEMANTIC).exists():
            return None

        rules = {
            rule.rule_key: rule
            for rule in cls.for_document(cls.Category.SEMANTIC, document_type)
        }
        aspects = []
        for default in DEFAULT_ASPECTS:
            rule = rules.get(default["key"])
            if rule is None:
                continue  # dinonaktifkan admin
            value = rule.rule_value if isinstance(rule.rule_value, dict) else {}
            aspects.append({
                "key": default["key"],
                "label": value.get("label") or default["label"],
                "instruction": value.get("instruction") or default["instruction"],
            })
        return aspects

    def __str__(self):
        label = self.get_document_type_display() if self.document_type else "Umum"
        return f"{self.rule_key} ({label})"


class RuleVersion(models.Model):
    """
    Catatan setiap perubahan aturan/instruksi AI dari Web Dashboard.
    Nomor versi (id) disimpan di setiap analisis (AIRun) sehingga kinerja
    AI sebelum & sesudah perubahan aturan bisa dibandingkan.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rule_versions",
    )
    note = models.CharField(max_length=255, blank=True, default="")
    # [{"rule_id", "rule_key", "category", "document_type", "before", "after"}]
    changes = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-id"]

    @classmethod
    def current(cls):
        """Nomor versi aturan yang sedang berlaku (0 = aturan awal)."""
        latest = cls.objects.order_by("-id").values_list("id", flat=True).first()
        return latest or 0

    def __str__(self):
        return f"Versi {self.pk}: {self.note or 'perubahan aturan'}"