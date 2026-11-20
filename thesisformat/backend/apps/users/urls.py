from django.urls import path
from .views import ChangePasswordView, ProfileView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("me/password/", ChangePasswordView.as_view(), name="change_password"),
]
