# Generated by Django 3.2 on 2021-04-20 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0001_initial"),
        ("connector_airflow", "0002_indexing"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ComposerEnvironment",
            new_name="Environment",
        ),
        migrations.RenameModel(
            old_name="ComposerEnvironmentPermission",
            new_name="EnvironmentPermission",
        ),
        migrations.AlterModelOptions(
            name="environment",
            options={
                "ordering": ("hexa_name",),
                "verbose_name": "GCP Composer environment",
            },
        ),
        migrations.RenameField(
            model_name="environmentpermission",
            old_name="composer_environment",
            new_name="airflow_environment",
        ),
    ]
