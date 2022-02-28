# Generated by Django 4.0.2 on 2022-02-28 11:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_accessmod", "0014_am_airflow_connect"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="accessibilityanalysis",
            name="extent",
        ),
        migrations.AddField(
            model_name="project",
            name="extent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="connector_accessmod.fileset",
            ),
        ),
    ]
