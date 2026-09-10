from django.urls import path

from .views import StalingramLoginView, StalingramLogoutView, register

app_name = "accounts"

urlpatterns = [
    path("login/", StalingramLoginView.as_view(), name="login"),
    path("register/", register, name="register"),
    path("logout/", StalingramLogoutView.as_view(), name="logout"),
]
