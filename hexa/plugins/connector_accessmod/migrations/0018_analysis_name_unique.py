# Generated by Django 4.0.2 on 2022-03-06 19:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0017_alter_accessibilityanalysis_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analysis",
            name="name",
            field=models.TextField(unique=True),
        ),
    ]
