
from django.urls import path
from .views import DocumentUploadView, DocumentHistoryView

urlpatterns = [
    path(
        "upload/",
        DocumentUploadView.as_view(),
        name="document-upload",
    ),
    path(
        "history/",
        DocumentHistoryView.as_view(),
        name="document-history",
    ),
]
