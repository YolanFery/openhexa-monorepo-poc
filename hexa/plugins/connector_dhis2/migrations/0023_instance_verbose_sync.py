# Generated by Django 3.2.7 on 2021-12-19 10:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_dhis2", "0022_organisationunit_datasets"),
    ]

    operations = [
        migrations.AddField(
            model_name="instance",
            name="verbose_sync",
            field=models.BooleanField(default=False),
        ),
    ]
