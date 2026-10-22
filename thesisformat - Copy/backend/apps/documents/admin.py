from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "document_type",
        "status",
        "uploaded_at",
    )

    search_fields = (
        "title",
        "user__username",
    )

    list_filter = (
        "document_type",
        "status",
        "uploaded_at",
    )