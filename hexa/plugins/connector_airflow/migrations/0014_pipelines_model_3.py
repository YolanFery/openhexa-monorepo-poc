# Generated by Django 3.2 on 2021-04-24 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connector_airflow', '0013_pipelines_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dagconfigrun',
            options={'ordering': ('-hexa_last_refreshed_at',)},
        ),
        migrations.AlterField(
            model_name='dagconfigrun',
            name='state',
            field=models.CharField(choices=[('success', 'Success'), ('running', 'Running'), ('failed', 'Failed')], max_length=200),
        ),
    ]
