# Generated by Django 5.0 on 2023-12-29 10:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0017_alter_user_email"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="accepted_tos",
        ),
    ]
