# Generated by Django 4.0.6 on 2022-09-01 10:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0013_alter_user_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"ordering": ["last_name"]},
        ),
    ]
