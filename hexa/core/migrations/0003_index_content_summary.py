# Generated by Django 3.2 on 2021-04-27 22:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="index",
            name="content_summary",
            field=models.TextField(blank=True),
        ),
    ]
