# Generated by Django 4.1.3 on 2022-12-21 15:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0014_alter_user_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="featureflag",
            name="feature",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="user_management.feature",
            ),
        ),
    ]
