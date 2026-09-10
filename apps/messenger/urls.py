from django.urls import path

from . import views

app_name = "messenger"

urlpatterns = [
    path("", views.home, name="home"),
    path("contacts/", views.contacts, name="contacts"),
    path("contacts/<str:username>/add/", views.add_contact, name="add_contact"),
    path("contacts/<str:username>/remove/", views.remove_contact, name="remove_contact"),
    path("chat/start/<str:username>/", views.start_chat, name="start_chat"),
    path("chat/<int:chat_id>/", views.chat_detail, name="chat"),
    path("chat/<int:chat_id>/send/", views.send_message, name="send_message"),
    path("chat/<int:chat_id>/poll/", views.poll_messages, name="poll_messages"),
]
