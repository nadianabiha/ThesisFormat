from django.contrib import admin

from .models import AuditResult


@admin.register(AuditResult)
class AuditResultAdmin(admin.ModelAdmin):
    list_display = (
        "document",
        "physical_score",
        "semantic_score",
        "final_score",
        "review_status",
        "corrected_score",
        "created_at",
    )

    search_fields = (
        "document__title",
    )

    list_filter = (
        "review_status",
        "created_at",
    )
