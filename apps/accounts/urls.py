from django.urls import path

from .views import (
    StalingramLoginView,
    StalingramLogoutView,
    StalingramPasswordChangeView,
    profile,
    public_profile,
    register,
    remove_avatar,
)

app_name = "accounts"

urlpatterns = [
    path("login/", StalingramLoginView.as_view(), name="login"),
    path("register/", register, name="register"),
    path("logout/", StalingramLogoutView.as_view(), name="logout"),
    path("profile/", profile, name="profile"),
    path("profile/avatar/remove/", remove_avatar, name="remove_avatar"),
    path(
        "profile/password/",
        StalingramPasswordChangeView.as_view(),
        name="password_change",
    ),
    path("u/<str:username>/", public_profile, name="public_profile"),
]
