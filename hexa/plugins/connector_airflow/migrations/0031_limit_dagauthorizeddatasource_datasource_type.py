# Generated by Django 4.0.2 on 2022-03-11 08:00

import django.db.models.deletion
from django.db import migrations, models

import hexa.plugins.connector_airflow.models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("connector_airflow", "0030_dagauthorizeddatasource_unique_together_dag_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dagauthorizeddatasource",
            name="datasource_type",
            field=models.ForeignKey(
                limit_choices_to=hexa.plugins.connector_airflow.models.limit_data_source_types,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
    ]
