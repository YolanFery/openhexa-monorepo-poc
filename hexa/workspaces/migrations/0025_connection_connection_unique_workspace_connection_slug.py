# Generated by Django 4.1.7 on 2023-03-31 11:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0024_alter_workspace_db_name"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="connection",
            constraint=models.UniqueConstraint(
                models.F("workspace"),
                models.F("slug"),
                name="connection_unique_workspace_connection_slug",
            ),
        ),
    ]
