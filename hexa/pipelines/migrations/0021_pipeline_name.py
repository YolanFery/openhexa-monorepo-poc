# Generated by Django 4.1.7 on 2023-03-30 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pipelines", "0020_rename_name_pipeline_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="pipeline",
            name="name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
