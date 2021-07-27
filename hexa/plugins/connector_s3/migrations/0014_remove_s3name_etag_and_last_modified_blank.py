# Generated by Django 3.2.5 on 2021-07-27 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_s3", "0013_object_orphan"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="object",
            name="s3_name",
        ),
        migrations.AlterField(
            model_name="object",
            name="s3_etag",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="object",
            name="s3_last_modified",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
