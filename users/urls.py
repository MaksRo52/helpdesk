from django.contrib.auth.views import LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import (CustomLoginView, CustomPasswordChangeView,
                         RecoveryPasswordView, UserCreateView, UserProfileView,
                         UserUpdateView, developer ) # email_verification

app_name = UsersConfig.name

urlpatterns = [
    path("login/", CustomLoginView.as_view(template_name="login.html"), name="login"),
    path(
        "activate_account/",
        CustomLoginView.as_view(template_name="activate.html"),
        name="activate_account",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    # path("activate/<str:token>/", email_verification, name="activate"),
    path("recovery/", RecoveryPasswordView.as_view(), name="recovery"),
    path(
        "profile/<int:pk>/", UserProfileView.as_view(), name="profile"
    ),  # Для показа профиля
    path(
        "profile/update/<int:pk>/", UserUpdateView.as_view(), name="profile_update"
    ),  # Для редактирования профиля
    path(
        "profile/password_change/",
        CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path("developer/", developer, name="developer"),
]
