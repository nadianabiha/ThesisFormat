
from django.urls import path
from .views import DocumentUploadView, DocumentHistoryView, DocumentResultView

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
        "history/",
        DocumentHistoryView.as_view(),
        name="document-history",
    ),
]
