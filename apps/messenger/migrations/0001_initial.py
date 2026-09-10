import apps.messenger.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Chat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("direct_key", models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={"ordering": ("-updated_at", "-id")},
        ),
        migrations.CreateModel(
            name="Contact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contact_links", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contact_of", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("created_at",)},
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(blank=True, max_length=4096)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("edited_at", models.DateTimeField(blank=True, null=True)),
                ("chat", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="messenger.chat")),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sent_messages", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("id",)},
        ),
        migrations.CreateModel(
            name="ChatParticipant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("chat", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="messenger.chat")),
                ("last_read_message", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="read_by_memberships", to="messenger.message")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chat_memberships", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name="chat",
            name="participants",
            field=models.ManyToManyField(related_name="messenger_chats", through="messenger.ChatParticipant", to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name="MessageAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to=apps.messenger.models.message_attachment_path)),
                ("kind", models.CharField(choices=[("image", "Изображение"), ("video", "Видео"), ("audio", "Аудио"), ("file", "Файл")], default="file", max_length=16)),
                ("original_name", models.CharField(max_length=255)),
                ("mime_type", models.CharField(blank=True, max_length=127)),
                ("size", models.PositiveBigIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("message", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="messenger.message")),
            ],
        ),
        migrations.AddConstraint(
            model_name="contact",
            constraint=models.UniqueConstraint(fields=("owner", "user"), name="unique_contact"),
        ),
        migrations.AddConstraint(
            model_name="chatparticipant",
            constraint=models.UniqueConstraint(fields=("chat", "user"), name="unique_chat_participant"),
        ),
    ]
