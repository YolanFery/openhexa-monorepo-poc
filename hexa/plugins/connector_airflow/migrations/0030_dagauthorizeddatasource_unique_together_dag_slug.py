# Generated by Django 4.0.2 on 2022-03-11 07:29

from django.db import migrations


def forward(apps, schema_editor):
    DAGAuthorizedDataSource = apps.get_model(
        "connector_airflow", "DAGAuthorizedDataSource"
    )
    DAGAuthorizedDataSource.objects.filter(slug="datasource").update(slug=None)


class Migration(migrations.Migration):
    dependencies = [
        ("connector_airflow", "0029_dagauthorizeddatasource_slug"),
    ]

    operations = [
        migrations.RunPython(forward, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name="dagauthorizeddatasource",
            unique_together={("dag", "slug")},
        ),
    ]
