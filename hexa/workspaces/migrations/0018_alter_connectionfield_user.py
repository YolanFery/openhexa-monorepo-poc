# Generated by Django 4.1.3 on 2023-03-07 12:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("workspaces", "0017_alter_workspace_db_name_alter_workspace_db_password"),
    ]

    operations = [
        migrations.AlterField(
            model_name="connectionfield",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
