# Generated by Django 4.1.7 on 2023-04-13 15:54

from django.db import migrations, models

import hexa.core.models.cryptography


class Migration(migrations.Migration):

    dependencies = [
        ("workspaces", "0025_connection_connection_unique_workspace_connection_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workspace",
            name="db_name",
            field=models.CharField(max_length=63, unique=True),
        ),
        migrations.AlterField(
            model_name="workspace",
            name="db_password",
            field=hexa.core.models.cryptography.EncryptedTextField(),
        ),
    ]
