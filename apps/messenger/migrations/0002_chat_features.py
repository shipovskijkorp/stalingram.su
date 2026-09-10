import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("messenger", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="chatparticipant",
            name="draft_text",
            field=models.TextField(blank=True, default="", max_length=4096),
        ),
        migrations.AddField(
            model_name="chatparticipant",
            name="draft_updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="chatparticipant",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="chatparticipant",
            name="is_muted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="chatparticipant",
            name="is_pinned",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="chatparticipant",
            name="last_typing_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="message",
            name="forwarded_from",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="forwarded_copies",
                to="messenger.message",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="forwarded_from_name",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AddField(
            model_name="message",
            name="forwarded_from_username",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="message",
            name="is_deleted",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="message",
            name="reply_to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="replies",
                to="messenger.message",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="updated_at",
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="message",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.CreateModel(
            name="PinnedMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pinned_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("chat", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pinned_messages", to="messenger.chat")),
                ("message", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pin_records", to="messenger.message")),
                ("pinned_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="pinned_chat_messages", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-pinned_at", "-id")},
        ),
        migrations.AddConstraint(
            model_name="pinnedmessage",
            constraint=models.UniqueConstraint(fields=("chat", "message"), name="unique_pinned_message"),
        ),
    ]
