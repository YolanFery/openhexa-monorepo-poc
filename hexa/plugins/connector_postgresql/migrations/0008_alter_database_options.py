# Generated by Django 3.2.7 on 2021-12-19 10:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("connector_postgresql", "0007_database_auto_sync"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="database",
            options={"ordering": ("hostname",), "verbose_name": "PostgreSQL Database"},
        ),
    ]
