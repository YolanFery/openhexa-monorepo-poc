# Generated by Django 3.2.7 on 2021-09-30 09:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("connector_airflow", "0010_auto_20210928_0926"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dagrun",
            options={"ordering": ("-execution_date",)},
        ),
    ]
