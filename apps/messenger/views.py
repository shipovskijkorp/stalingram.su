from pathlib import Path

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import BigIntegerField, Count, F, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from .forms import MessageForm
from .models import Chat, ChatParticipant, Contact, Message, MessageAttachment
from .services import (
    attachment_kind,
    get_or_create_direct_chat,
    mark_chat_read,
    serialize_message,
    touch_chat,
)

User = get_user_model()


def _safe_next(request, fallback):
    candidate = request.POST.get("next", "")
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return fallback


def _chat_for_user(user, chat_id):
    return get_object_or_404(
        Chat.objects.filter(participants=user).prefetch_related("participants"),
        pk=chat_id,
    )


def _prepare_sidebar_chats(user):
    last_message = Message.objects.filter(chat=OuterRef("pk")).order_by("-id")
    last_read = ChatParticipant.objects.filter(chat=OuterRef("pk"), user=user)

    chats = list(
        Chat.objects.filter(participants=user)
        .annotate(
            last_message_id_ui=Subquery(last_message.values("id")[:1]),
            last_message_text_ui=Subquery(last_message.values("text")[:1]),
            last_message_sender_id_ui=Subquery(last_message.values("sender_id")[:1]),
            last_message_created_at_ui=Subquery(last_message.values("created_at")[:1]),
            last_read_message_id_ui=Coalesce(
                Subquery(
                    last_read.values("last_read_message_id")[:1],
                    output_field=BigIntegerField(),
                ),
                Value(0, output_field=BigIntegerField()),
            ),
        )
        .annotate(
            unread_count_ui=Count(
                "messages",
                filter=(
                    ~Q(messages__sender=user)
                    & Q(messages__id__gt=F("last_read_message_id_ui"))
                ),
            )
        )
        .prefetch_related("participants")
        .order_by(F("last_message_created_at_ui").desc(nulls_last=True), "-updated_at")
    )

    for chat in chats:
        chat.other_user = next(
            (participant for participant in chat.participants.all() if participant.pk != user.pk),
            user,
        )
        preview = " ".join((chat.last_message_text_ui or "").split())
        chat.last_message_preview_ui = preview or "Медиа"
    return chats


def _messenger_context(user, selected_chat=None, chat_messages=None, message_form=None):
    return {
        "chats": _prepare_sidebar_chats(user),
        "selected_chat": selected_chat,
        "chat_messages": chat_messages or [],
        "message_form": message_form or MessageForm(),
    }


@login_required
def home(request):
    return render(request, "messenger/index.html", _messenger_context(request.user))


@login_required
def chat_detail(request, chat_id):
    chat = _chat_for_user(request.user, chat_id)
    latest = chat.messages.order_by("-id").first()
    if latest:
        mark_chat_read(chat, request.user, latest)

    messages_qs = list(
        chat.messages.select_related("sender")
        .prefetch_related("attachments")
        .order_by("-id")[:100]
    )
    messages_qs.reverse()
    chat.other_user = next(
        participant for participant in chat.participants.all() if participant.pk != request.user.pk
    )
    return render(
        request,
        "messenger/index.html",
        _messenger_context(request.user, chat, messages_qs),
    )


@login_required
@require_POST
def start_chat(request, username):
    target = get_object_or_404(User, username__iexact=username, is_active=True)
    if target.pk == request.user.pk:
        messages.info(request, "Чат с самим собой пока не используется как «Избранное».")
        return redirect("accounts:public_profile", username=request.user.username)
    chat = get_or_create_direct_chat(request.user, target)
    return redirect("messenger:chat", chat_id=chat.pk)


@login_required
def contacts(request):
    query = request.GET.get("q", "").strip().lstrip("@")[:150]
    contact_links = list(
        Contact.objects.filter(owner=request.user)
        .select_related("user")
        .order_by("user__username")
    )
    contact_ids = {item.user_id for item in contact_links}

    search_results = []
    if query:
        search_results = list(
            User.objects.filter(is_active=True, username__icontains=query)
            .exclude(pk=request.user.pk)
            .order_by("username")[:30]
        )
        for user in search_results:
            user.is_contact_ui = user.pk in contact_ids

    return render(
        request,
        "messenger/contacts.html",
        {
            "contacts": contact_links,
            "query": query,
            "search_results": search_results,
            "focus_search": request.GET.get("focus") == "search",
        },
    )


@login_required
@require_POST
def add_contact(request, username):
    target = get_object_or_404(User, username__iexact=username, is_active=True)
    if target.pk != request.user.pk:
        Contact.objects.get_or_create(owner=request.user, user=target)
        messages.success(request, f"@{target.username} добавлен в контакты.")
    return redirect(_safe_next(request, reverse("messenger:contacts")))


@login_required
@require_POST
def remove_contact(request, username):
    target = get_object_or_404(User, username__iexact=username, is_active=True)
    Contact.objects.filter(owner=request.user, user=target).delete()
    messages.success(request, f"@{target.username} удалён из контактов.")
    return redirect(_safe_next(request, reverse("messenger:contacts")))


@login_required
@require_POST
def send_message(request, chat_id):
    chat = _chat_for_user(request.user, chat_id)
    form = MessageForm(request.POST, request.FILES)
    wants_json = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if not form.is_valid():
        if wants_json:
            return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)
        for error in form.non_field_errors():
            messages.error(request, error)
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
        return redirect("messenger:chat", chat_id=chat.pk)

    attachment_mode = form.cleaned_data.get("attachment_mode") or MessageForm.MODE_MEDIA
    send_as_file = attachment_mode == MessageForm.MODE_FILE

    with transaction.atomic():
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            text=form.cleaned_data["text"],
        )
        for uploaded in form.cleaned_data["attachments"]:
            MessageAttachment.objects.create(
                message=message,
                file=uploaded,
                kind=(
                    MessageAttachment.Kind.FILE
                    if send_as_file
                    else attachment_kind(uploaded)
                ),
                original_name=Path(uploaded.name).name[:255],
                mime_type=(getattr(uploaded, "content_type", "") or "")[:127],
                size=uploaded.size,
            )
        touch_chat(chat)
        mark_chat_read(chat, request.user, message)

    message = (
        Message.objects.select_related("sender")
        .prefetch_related("attachments")
        .get(pk=message.pk)
    )
    if wants_json:
        return JsonResponse({"ok": True, "message": serialize_message(message, request.user)})
    return redirect("messenger:chat", chat_id=chat.pk)


@login_required
@require_GET
def poll_messages(request, chat_id):
    chat = _chat_for_user(request.user, chat_id)
    try:
        after_id = max(0, int(request.GET.get("after", "0")))
    except (TypeError, ValueError):
        after_id = 0

    new_messages = list(
        chat.messages.filter(id__gt=after_id)
        .select_related("sender")
        .prefetch_related("attachments")
        .order_by("id")[:100]
    )
    if new_messages:
        mark_chat_read(chat, request.user, new_messages[-1])

    return JsonResponse(
        {
            "ok": True,
            "messages": [serialize_message(message, request.user) for message in new_messages],
        }
    )
