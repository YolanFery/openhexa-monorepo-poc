# Generated by Django 4.0 on 2021-12-27 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0005_user_accepted_tos"),
    ]

    operations = [
        migrations.AddField(
            model_name="feature",
            name="force_activate",
            field=models.BooleanField(default=False),
        ),
    ]
