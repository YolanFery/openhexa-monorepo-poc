# Generated by Django 3.2.7 on 2021-10-27 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_airflow", "0012_remove_airflow_run_message"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dagrun",
            options={"ordering": ("-execution_date",)},
        ),
        migrations.AlterField(
            model_name="dagrun",
            name="state",
            field=models.CharField(
                choices=[
                    ("success", "Success"),
                    ("running", "Running"),
                    ("failed", "Failed"),
                    ("queued", "Queued"),
                ],
                max_length=200,
            ),
        ),
    ]
