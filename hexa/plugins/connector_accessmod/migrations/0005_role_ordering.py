# Generated by Django 4.0.1 on 2022-02-03 13:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0004_fileset_ordering"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="filesetrole",
            options={"ordering": ["name"]},
        ),
    ]
