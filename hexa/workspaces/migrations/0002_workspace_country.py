# Generated by Django 4.1.3 on 2022-12-21 09:23

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspace",
            name="country",
            field=django_countries.fields.CountryField(blank=True, max_length=2),
        ),
    ]
