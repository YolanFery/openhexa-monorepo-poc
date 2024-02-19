# Generated by Django 4.0.4 on 2022-05-12 10:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_accessmod", "0035_remove_accessibilityanalysis_max_slope_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filesetrole",
            name="code",
            field=models.CharField(
                choices=[
                    ("BARRIER", "Barrier"),
                    ("CATCHMENT_AREAS", "Catchment Areas"),
                    ("COVERAGE", "Coverage"),
                    ("DEM", "Dem"),
                    ("FRICTION_SURFACE", "Friction Surface"),
                    ("GEOMETRY", "Geometry"),
                    ("HEALTH_FACILITIES", "Health Facilities"),
                    ("LAND_COVER", "Land Cover"),
                    ("MOVING_SPEEDS", "Moving Speeds"),
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
