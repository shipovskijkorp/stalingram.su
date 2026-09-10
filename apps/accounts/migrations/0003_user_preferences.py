from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_user_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="enter_to_send",
            field=models.BooleanField(default=True, verbose_name="отправка по Enter"),
        ),
        migrations.AddField(
            model_name="user",
            name="theme",
            field=models.CharField(
                choices=[("light", "Светлая"), ("dark", "Тёмная")],
                default="light",
                max_length=10,
                verbose_name="тема оформления",
            ),
        ),
    ]
