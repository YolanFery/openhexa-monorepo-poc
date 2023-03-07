# Generated by Django 4.1.3 on 2023-03-06 13:58
import hashlib

from django.db import migrations, models


def generate_hash(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    WorkspaceMembership = apps.get_model("workspaces", "WorkspaceMembership")
    for membership in WorkspaceMembership.objects.all():
        membership.notebooks_server_hash = hashlib.blake2s(
            f"{membership.workspace_id}_{membership.user_id}".encode("utf-8"),
            digest_size=16,
        ).hexdigest()
        membership.save()


class Migration(migrations.Migration):

    dependencies = [
        ("workspaces", "0017_alter_workspace_db_name_alter_workspace_db_password"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspacemembership",
            name="notebooks_server_hash",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.RunPython(generate_hash, reverse_code=migrations.RunPython.noop),
    ]
