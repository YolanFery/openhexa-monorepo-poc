# Generated by Django 4.1.3 on 2023-02-07 14:33

import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workspaces", "0008_alter_workspace_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workspace",
            name="slug",
            field=models.CharField(
                editable=False,
                max_length=30,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-a-z0-9]+\\Z"),
                        "Enter a valid “slug” consisting of letters, numbers or hyphens.",
                        "invalid",
                    )
                ],
            ),
        ),
    ]
