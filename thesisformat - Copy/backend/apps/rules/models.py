from django.db import models


class MasterRule(models.Model):

    class Category(models.TextChoices):
        PHYSICAL = "physical", "Physical"
        SEMANTIC = "semantic", "Semantic"

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
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

    def __str__(self):
        return self.rule_key