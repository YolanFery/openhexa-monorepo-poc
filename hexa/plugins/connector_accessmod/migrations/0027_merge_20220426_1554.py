# Generated by Django 4.0.4 on 2022-04-26 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_accessmod", "0021_validatefilesetjob_fileset_status"),
        ("connector_accessmod", "0026_project_description_optional"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fileset",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("VALIDATING", "Validating"),
                    ("VALID", "Valid"),
                    ("INVALID", "Invalid"),
                ],
                default="PENDING",
                max_length=50,
            ),
        ),
    ]
