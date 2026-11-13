from django.contrib import admin

from .models import MasterRule


@admin.register(MasterRule)
class MasterRuleAdmin(admin.ModelAdmin):
    list_display = (
        "rule_key",
        "document_type",
        "category",
        "active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "rule_key",
        "description",
    )

    list_filter = (
        "document_type",
        "category",
        "active",
    )