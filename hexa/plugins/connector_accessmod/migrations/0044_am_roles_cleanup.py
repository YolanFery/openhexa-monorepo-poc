# Generated by Django 4.0.4 on 2022-05-22 05:18

from django.db import migrations, models


def forward(apps, schema_editor):
    Fileset = apps.get_model("connector_accessmod", "Fileset")
    FilesetRole = apps.get_model("connector_accessmod", "FilesetRole")

    Fileset.objects.filter(role__code__in=["CATCHMENT_AREAS", "MOVING_SPEEDS"]).delete()
    FilesetRole.objects.filter(code__in=["CATCHMENT_AREAS", "MOVING_SPEEDS"]).delete()


def reverse(apps, schema_editor):
    FilesetRole = apps.get_model("connector_accessmod", "FilesetRole")

    for (name, code, format) in [
        ("Catchment Areas", "CATCHMENT_AREAS", "VECTOR"),
        ("Moving speeds", "MOVING_SPEEDS", "TABULAR"),
    ]:
        FilesetRole.objects.get_or_create(
            name=name, format=format, defaults={"code": code}
        )


class Migration(migrations.Migration):

    dependencies = [
        ("connector_accessmod", "0043_am_fileset_mode"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=reverse),
        migrations.AlterField(
            model_name="filesetrole",
            name="code",
            field=models.CharField(
                choices=[
                    ("BARRIER", "Barrier"),
                    ("COVERAGE", "Coverage"),
                    ("DEM", "Dem"),
                    ("FRICTION_SURFACE", "Friction Surface"),
                    ("GEOMETRY", "Geometry"),
                    ("HEALTH_FACILITIES", "Health Facilities"),
                    ("LAND_COVER", "Land Cover"),
                    ("POPULATION", "Population"),
                    ("TRANSPORT_NETWORK", "Transport Network"),
                    ("TRAVEL_TIMES", "Travel Times"),
                    ("WATER", "Water"),
                    ("STACK", "Stack"),
                ],
                max_length=50,
            ),
        ),
    ]
