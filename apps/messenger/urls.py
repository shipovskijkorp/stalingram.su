from django.urls import path

from .views import home

app_name = "messenger"

urlpatterns = [
    path("", home, name="home"),
]
