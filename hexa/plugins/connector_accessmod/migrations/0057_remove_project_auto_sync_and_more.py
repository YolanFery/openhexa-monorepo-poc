# Generated by Django 4.1.3 on 2022-12-07 09:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0056_access_request_not_unique"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="auto_sync",
        ),
        migrations.RemoveField(
            model_name="project",
            name="last_synced_at",
        ),
        migrations.RemoveField(
            model_name="project",
            name="public",
        ),
    ]
