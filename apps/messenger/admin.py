from django.contrib import admin

from .models import Chat, ChatParticipant, Contact, Message, MessageAttachment


class ChatParticipantInline(admin.TabularInline):
    model = ChatParticipant
    extra = 0


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "direct_key", "updated_at")
    search_fields = ("direct_key",)
    inlines = (ChatParticipantInline,)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("owner", "user", "created_at")
    search_fields = ("owner__username", "user__username")


class MessageAttachmentInline(admin.TabularInline):
    model = MessageAttachment
    extra = 0


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "sender", "created_at")
    search_fields = ("sender__username", "text")
    inlines = (MessageAttachmentInline,)
