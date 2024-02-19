# Generated by Django 4.0.2 on 2022-03-01 14:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0016_am_file_proj_unique"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="accessibilityanalysis",
            options={"verbose_name_plural": "Accessibility analyses"},
        ),
        migrations.AlterField(
            model_name="project",
            name="name",
            field=models.TextField(verbose_name="project name"),
        ),
    ]
