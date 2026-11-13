from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import ThesisFormatTokenView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", ThesisFormatTokenView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/users/", include("apps.users.urls")),
    path("api/v1/documents/", include("apps.documents.urls")),
    # Web Dashboard (khusus admin/staf).
    path("api/v1/admin/", include("apps.audits.urls")),
]
