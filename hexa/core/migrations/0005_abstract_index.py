# Generated by Django 3.2.3 on 2021-05-27 09:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_minor_fine_tuning"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="index",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="index",
            name="owner",
        ),
        migrations.RemoveField(
            model_name="index",
            name="parent",
        ),
    ]
