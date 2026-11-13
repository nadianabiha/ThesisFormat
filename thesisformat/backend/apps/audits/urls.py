from django.urls import path

from .ai_views import (
    AdminDocumentReanalyzeView,
    AIPerformanceView,
    RetestCandidatesView,
    RuleDetailView,
    RuleListView,
)
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
    path(
        "documents/<int:pk>/reanalyze/",
        AdminDocumentReanalyzeView.as_view(),
        name="admin-document-reanalyze",
    ),
    # Pengawasan & perbaikan kualitas AI.
    path("ai-performance/", AIPerformanceView.as_view(), name="admin-ai-performance"),
    path(
        "ai-performance/retest-candidates/",
        RetestCandidatesView.as_view(),
        name="admin-ai-retest-candidates",
    ),
    path("rules/", RuleListView.as_view(), name="admin-rules"),
    path("rules/<int:pk>/", RuleDetailView.as_view(), name="admin-rule-detail"),
]
