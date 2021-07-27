# Generated by Django 3.2.5 on 2021-07-27 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_s3", "0016_alter_object_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="object",
            name="parent",
        ),
        migrations.AddField(
            model_name="object",
            name="s3_dirname",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]
