# Generated by Django 3.2.3 on 2021-06-11 12:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0006_concrete_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="catalogindex",
            name="external_name",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="catalogindex",
            name="external_short_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="catalogindex",
            name="name",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="catalogindex",
            name="short_name",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
