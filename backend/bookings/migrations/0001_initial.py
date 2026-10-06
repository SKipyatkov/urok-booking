# Generated manually for MVP

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("organizations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("parent_name", models.CharField(max_length=200, verbose_name="Имя родителя")),
                ("parent_email", models.EmailField(max_length=254, verbose_name="Email родителя")),
                ("parent_phone", models.CharField(max_length=30, verbose_name="Телефон")),
                ("child_name", models.CharField(max_length=200, verbose_name="Имя ребёнка")),
                ("child_age", models.PositiveSmallIntegerField(verbose_name="Возраст ребёнка")),
                ("notes", models.TextField(blank=True, verbose_name="Комментарий")),
                ("status", models.CharField(choices=[("new", "Новый"), ("trial", "Пробный"), ("active", "Учится"), ("rejected", "Отказ")], default="new", max_length=20, verbose_name="Статус")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="students", to="organizations.organization", verbose_name="Организация")),
            ],
            options={
                "verbose_name": "Ученик",
                "verbose_name_plural": "Ученики",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AvailabilityRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weekday", models.PositiveSmallIntegerField(help_text="0 — понедельник, 6 — воскресенье", verbose_name="День недели (0=пн)")),
                ("start_time", models.TimeField(verbose_name="Начало")),
                ("end_time", models.TimeField(verbose_name="Конец")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="availability_rules", to="organizations.teacher", verbose_name="Преподаватель")),
            ],
            options={
                "verbose_name": "Правило доступности",
                "verbose_name_plural": "Правила доступности",
                "ordering": ["weekday", "start_time"],
            },
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("starts_at", models.DateTimeField(verbose_name="Начало")),
                ("ends_at", models.DateTimeField(verbose_name="Конец")),
                ("type", models.CharField(choices=[("trial", "Пробный"), ("regular", "Регулярный")], default="trial", max_length=20, verbose_name="Тип")),
                ("status", models.CharField(choices=[("pending", "Ожидает"), ("confirmed", "Подтверждён"), ("cancelled", "Отменён"), ("completed", "Завершён")], default="pending", max_length=20, verbose_name="Статус")),
                ("meeting_url", models.URLField(blank=True, verbose_name="Ссылка на занятие")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookings", to="organizations.organization", verbose_name="Организация")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookings", to="bookings.student", verbose_name="Ученик")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookings", to="organizations.teacher", verbose_name="Преподаватель")),
            ],
            options={
                "verbose_name": "Бронирование",
                "verbose_name_plural": "Бронирования",
                "ordering": ["starts_at"],
            },
        ),
        migrations.CreateModel(
            name="BlockedSlot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("starts_at", models.DateTimeField(verbose_name="Начало")),
                ("ends_at", models.DateTimeField(verbose_name="Конец")),
                ("reason", models.CharField(blank=True, max_length=200, verbose_name="Причина")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocked_slots", to="organizations.teacher", verbose_name="Преподаватель")),
            ],
            options={
                "verbose_name": "Заблокированный слот",
                "verbose_name_plural": "Заблокированные слоты",
                "ordering": ["starts_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="booking",
            constraint=models.UniqueConstraint(fields=("teacher", "starts_at"), name="unique_teacher_starts_at"),
        ),
    ]
