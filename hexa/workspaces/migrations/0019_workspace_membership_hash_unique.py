# Generated by Django 4.1.3 on 2023-03-06 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workspaces", "0018_workspace_membership_hash"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workspacemembership",
            name="notebooks_server_hash",
            field=models.TextField(unique=True),
        ),
    ]
