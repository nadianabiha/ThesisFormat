from django.urls import path

from .views import (
    AdminDocumentDetailView,
    AdminDocumentListView,
    AdminDocumentReviewView,
    AdminStatsView,
    AdminStudentListView,
)

urlpatterns = [
    path("stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("students/", AdminStudentListView.as_view(), name="admin-students"),
    path("documents/", AdminDocumentListView.as_view(), name="admin-documents"),
    path(
        "documents/<int:pk>/",
        AdminDocumentDetailView.as_view(),
        name="admin-document-detail",
    ),
    path(
        "documents/<int:pk>/review/",
        AdminDocumentReviewView.as_view(),
        name="admin-document-review",
    ),
]
