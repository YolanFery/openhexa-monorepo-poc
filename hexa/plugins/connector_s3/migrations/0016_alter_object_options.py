# Generated by Django 3.2.5 on 2021-07-27 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("connector_s3", "0015_alter_bucket_tags"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="object",
            options={"ordering": ["s3_key"], "verbose_name": "S3 Object"},
        ),
    ]
