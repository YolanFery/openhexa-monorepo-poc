# Generated by Django 3.2.4 on 2021-06-17 07:18

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0008_tags"),
    ]

    operations = [TrigramExtension()]
