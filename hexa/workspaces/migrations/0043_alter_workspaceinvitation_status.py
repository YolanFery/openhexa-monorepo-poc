# Generated by Django 4.1.7 on 2023-12-29 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workspaces", "0042_set_workspace_created_by"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workspaceinvitation",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("DECLINED", "Declined"),
                    ("ACCEPTED", "Accepted"),
                ],
                default="PENDING",
                max_length=50,
            ),
        ),
    ]
