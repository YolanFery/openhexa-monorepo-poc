# Generated by Django 3.2.4 on 2021-06-17 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_tags"),
        ("connector_s3", "0007_longer_text_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="object",
            name="tags",
            field=models.ManyToManyField(to="catalog.Tag"),
        ),
    ]
