# Generated by Django 4.1.7 on 2023-03-30 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pipelines", "0019_alter_pipeline_name_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="pipeline",
            old_name="name",
            new_name="code",
        ),
    ]
