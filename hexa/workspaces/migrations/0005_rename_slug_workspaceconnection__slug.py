# Generated by Django 4.1.3 on 2023-01-12 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("workspaces", "0004_workspaceconnection_workspaceconnectionfield"),
    ]

    operations = [
        migrations.RenameField(
            model_name="workspaceconnection",
            old_name="slug",
            new_name="_slug",
        ),
    ]
