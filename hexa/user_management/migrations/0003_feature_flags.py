# Generated by Django 3.2.6 on 2021-09-10 11:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0002_remove_username"),
    ]

    operations = [
        migrations.CreateModel(
            name="Feature",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=200)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="FeatureFlag",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("config", models.JSONField(blank=True, null=True)),
                (
                    "feature",
                    models.ForeignKey(
                        on_delete=django.db.models.fields.CharField,
                        to="user_management.feature",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
