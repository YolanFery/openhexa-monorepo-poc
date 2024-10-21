# Generated by Django 5.0.8 on 2024-10-21 07:48

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0010_datasetversionfile_properties"),
    ]

    operations = [
        migrations.AlterField(
            model_name="datasetfilesample",
            name="sample",
            field=models.JSONField(
                blank=True,
                default=list,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
                null=True,
            ),
        ),
    ]
