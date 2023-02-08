# Generated by Django 4.1.3 on 2023-02-08 13:33

import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workspaces", "0014_merge_20230208_1017"),
    ]

    operations = [
        migrations.AlterField(
            model_name="connectionfield",
            name="code",
            field=models.CharField(
                max_length=30,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-a-zA-Z0-9_]+\\Z"),
                        "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.",
                        "invalid",
                    )
                ],
            ),
        ),
    ]
