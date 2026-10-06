# Generated manually for MVP

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Название")),
                ("slug", models.SlugField(max_length=100, unique=True, verbose_name="Slug")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("contact_email", models.EmailField(max_length=254, verbose_name="Контактный email")),
                ("timezone", models.CharField(default="Europe/Moscow", max_length=63, verbose_name="Часовой пояс")),
                ("slot_duration_minutes", models.PositiveSmallIntegerField(choices=[(30, "30 минут"), (60, "60 минут")], default=60, verbose_name="Длительность слота (мин)")),
                ("plan", models.CharField(choices=[("free_trial", "Пробный"), ("solo", "Соло"), ("school", "Школа")], default="free_trial", max_length=20, verbose_name="Тариф")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Организация",
                "verbose_name_plural": "Организации",
            },
        ),
        migrations.CreateModel(
            name="Teacher",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Имя")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="teachers", to="organizations.organization", verbose_name="Организация")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="teacher_profile", to=settings.AUTH_USER_MODEL, verbose_name="Пользователь")),
            ],
            options={
                "verbose_name": "Преподаватель",
                "verbose_name_plural": "Преподаватели",
            },
        ),
    ]
