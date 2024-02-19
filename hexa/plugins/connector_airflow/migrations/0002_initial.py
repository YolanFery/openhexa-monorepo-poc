# Generated by Django 3.2 on 2021-04-26 12:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("user_management", "0001_initial"),
        ("connector_airflow", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="dagconfig",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user_management.organization",
            ),
        ),
        migrations.AddField(
            model_name="dag",
            name="cluster",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="connector_airflow.cluster",
            ),
        ),
        migrations.AddField(
            model_name="dag",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user_management.organization",
            ),
        ),
        migrations.AddField(
            model_name="credentials",
            name="team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="airflow_credential_set",
                to="user_management.team",
            ),
        ),
        migrations.AddField(
            model_name="clusterpermission",
            name="cluster",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="connector_airflow.cluster",
            ),
        ),
        migrations.AddField(
            model_name="clusterpermission",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="user_management.team"
            ),
        ),
        migrations.AddField(
            model_name="cluster",
            name="api_credentials",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="connector_airflow.credentials",
            ),
        ),
        migrations.AddField(
            model_name="cluster",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user_management.organization",
            ),
        ),
    ]
