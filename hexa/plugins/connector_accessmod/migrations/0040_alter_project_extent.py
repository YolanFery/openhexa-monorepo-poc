# Generated by Django 4.0.4 on 2022-05-12 20:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0039_alter_project_extent2"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="extent",
            field=models.JSONField(default=list),
        ),
    ]
