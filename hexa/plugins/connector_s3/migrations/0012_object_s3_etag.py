# Generated by Django 3.2.5 on 2021-07-23 11:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_s3", "0011_allow_blank_parent_blank_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="object",
            name="s3_etag",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
