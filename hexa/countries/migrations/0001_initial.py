# Generated by Django 4.0.4 on 2022-05-22 21:27

import uuid

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
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
                ("name", models.TextField()),
                ("code", models.CharField(max_length=2)),
                ("alpha3", models.CharField(max_length=3)),
                (
                    "region",
                    models.CharField(
                        choices=[
                            ("AMRO", "Amro"),
                            ("AFRO", "Afro"),
                            ("EMRO", "Emro"),
                            ("EURO", "Euro"),
                            ("WPRO", "Wpro"),
                            ("SEARO", "Searo"),
                        ],
                        max_length=50,
                    ),
                ),
                ("default_crs", models.IntegerField()),
                (
                    "simplified_extent",
                    django.contrib.gis.db.models.fields.GeometryField(srid=4326),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
