# Generated by Django 4.1.7 on 2023-08-16 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pipelines", "0029_remove_pipeline_timeout_pipelineversion_timeout"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pipelineversion",
            name="timeout",
            field=models.IntegerField(
                help_text="Time (in seconds) after which the pipeline execution will be stopped (with a default value of 4 hours up to 12 max).",
                null=True,
            ),
        ),
    ]
