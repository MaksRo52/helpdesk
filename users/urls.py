from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import (RecoveryPasswordView, UserCreateView, UserProfileView,
                         email_verification)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("activate/<str:token>/", email_verification, name="activate"),
    path("recovery/", RecoveryPasswordView.as_view(), name="recovery"),
    path(
        "profile/<int:pk>/", UserProfileView.as_view(), name="profile"
    ),  # Для показа профиля
]
