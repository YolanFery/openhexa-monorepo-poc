# Generated by Django 3.1.7 on 2021-04-06 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connector_s3', '0007_fields_rename'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bucket',
            old_name='created_at',
            new_name='hexa_created_at',
        ),
        migrations.RenameField(
            model_name='bucket',
            old_name='updated_at',
            new_name='hexa_updated_at',
        ),
        migrations.RenameField(
            model_name='object',
            old_name='created_at',
            new_name='hexa_created_at',
        ),
        migrations.RenameField(
            model_name='object',
            old_name='updated_at',
            new_name='hexa_updated_at',
        ),
    ]
