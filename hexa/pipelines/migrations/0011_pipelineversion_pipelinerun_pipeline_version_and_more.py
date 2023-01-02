# Generated by Django 4.1.3 on 2023-01-02 14:49

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pipelines", "0010_alter_pipeline_options_pipeline_config_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PipelineVersion",
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
                ("number", models.SmallIntegerField()),
                ("zipfile", models.BinaryField()),
                (
                    "pipeline",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pipelines.pipeline",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-number",),
            },
        ),
        migrations.AddField(
            model_name="pipelinerun",
            name="pipeline_version",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="pipelines.pipelineversion",
            ),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="pipelineversion",
            constraint=models.UniqueConstraint(
                models.F("id"), models.F("number"), name="pipeline_unique_version"
            ),
        ),
    ]
