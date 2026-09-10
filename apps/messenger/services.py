from django.db import transaction
from django.utils import timezone

from .models import Chat, ChatParticipant, MessageAttachment


@transaction.atomic
def get_or_create_direct_chat(first_user, second_user):
    if first_user.pk == second_user.pk:
        raise ValueError("Cannot create a direct chat with yourself")

    low_id, high_id = sorted((first_user.pk, second_user.pk))
    direct_key = f"{low_id}:{high_id}"
    chat, created = Chat.objects.get_or_create(direct_key=direct_key)
    if created:
        ChatParticipant.objects.bulk_create(
            [
                ChatParticipant(chat=chat, user=first_user),
                ChatParticipant(chat=chat, user=second_user),
            ]
        )
    return chat


def mark_chat_read(chat, user, message=None):
    if message is None:
        message = chat.messages.order_by("-id").first()
    if message is None:
        return
    ChatParticipant.objects.filter(chat=chat, user=user).update(last_read_message=message)


def touch_chat(chat):
    Chat.objects.filter(pk=chat.pk).update(updated_at=timezone.now())


def attachment_kind(uploaded):
    content_type = (getattr(uploaded, "content_type", "") or "").lower()
    if content_type.startswith("image/"):
        return MessageAttachment.Kind.IMAGE
    if content_type.startswith("video/"):
        return MessageAttachment.Kind.VIDEO
    if content_type.startswith("audio/"):
        return MessageAttachment.Kind.AUDIO
    return MessageAttachment.Kind.FILE


def serialize_message(message, current_user):
    return {
        "id": message.pk,
        "text": message.text,
        "sender_id": message.sender_id,
        "sender_name": message.sender.display_name,
        "is_own": message.sender_id == current_user.pk,
        "created_at": message.created_at.isoformat(),
        "time": timezone.localtime(message.created_at).strftime("%H:%M"),
        "attachments": [
            {
                "id": attachment.pk,
                "kind": attachment.kind,
                "name": attachment.original_name,
                "url": attachment.file.url,
                "size": attachment.size,
            }
            for attachment in message.attachments.all()
        ],
    }
