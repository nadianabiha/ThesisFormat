
from django.urls import path
from .views import (
    DocumentHistoryView,
    DocumentRecheckView,
    DocumentResultView,
    DocumentUploadView,
)

urlpatterns = [
    path(
        "upload/",
        DocumentUploadView.as_view(),
        name="document-upload",
    ),
    path(
        "<int:pk>/result/",
        DocumentResultView.as_view(),
        name="document-result",
    ),
    path(
        "<int:pk>/recheck/",
        DocumentRecheckView.as_view(),
        name="document-recheck",
    ),
    path(
        "history/",
        DocumentHistoryView.as_view(),
        name="document-history",
    ),
]
