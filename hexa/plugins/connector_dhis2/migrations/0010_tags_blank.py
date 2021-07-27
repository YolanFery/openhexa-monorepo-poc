# Generated by Django 3.2.5 on 2021-07-27 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_tags"),
        ("connector_dhis2", "0009_datasource_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dataelement",
            name="tags",
            field=models.ManyToManyField(blank=True, to="catalog.Tag"),
        ),
        migrations.AlterField(
            model_name="indicator",
            name="tags",
            field=models.ManyToManyField(blank=True, to="catalog.Tag"),
        ),
        migrations.AlterField(
            model_name="indicatortype",
            name="tags",
            field=models.ManyToManyField(blank=True, to="catalog.Tag"),
        ),
    ]
