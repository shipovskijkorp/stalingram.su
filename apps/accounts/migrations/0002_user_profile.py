from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True,
                default="",
                upload_to="avatars/%Y/%m/",
                verbose_name="фотография профиля",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="bio",
            field=models.CharField(
                blank=True,
                default="",
                max_length=160,
                verbose_name="о себе",
            ),
        ),
    ]
