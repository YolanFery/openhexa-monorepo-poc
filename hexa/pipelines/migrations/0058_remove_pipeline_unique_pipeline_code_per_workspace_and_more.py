# Generated by Django 5.1.5 on 2025-02-24 21:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline_templates", "0007_pipelinetemplateversion_user_and_more"),
        (
            "pipelines",
            "0057_remove_pipeline_unique_pipeline_code_per_workspace_and_more",
        ),
        (
            "workspaces",
            "0044_remove_workspaceinvitation_workspace_invitation_unique_workspace_email",
        ),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="pipeline",
            name="unique_pipeline_code_per_workspace",
        ),
        migrations.AddConstraint(
            model_name="pipeline",
            constraint=models.UniqueConstraint(
                models.F("workspace_id"),
                models.F("code"),
                condition=models.Q(("deleted_at__isnull", True)),
                name="unique_pipeline_code_per_workspace",
                violation_error_message="A pipeline with the same code already exists in this workspace. Consider using `create_if_has_perm` method.",
            ),
        ),
    ]
