# Generated by Django 4.0.2 on 2022-02-21 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_accessmod", "0008_analysis_models"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="accessibilityanalysis",
            name="extent",
        ),
        migrations.AddField(
            model_name="accessibilityanalysis",
            name="invert_direction",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="accessibilityanalysis",
            name="anisotropic",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="accessibilityanalysis",
            name="max_travel_time",
            field=models.IntegerField(default=360, null=True),
        ),
        migrations.AlterField(
            model_name="filesetrole",
            name="code",
            field=models.CharField(
                choices=[
                    ("BARRIER", "Barrier"),
                    ("DEM", "Dem"),
                    ("FRICTION_SURFACE", "Friction Surface"),
                    ("GEOMETRY", "Geometry"),
                    ("HEALTH_FACILITIES", "Health Facilities"),
                    ("LAND_COVER", "Land Cover"),
                    ("MOVING_SPEEDS", "Moving Speeds"),
                    ("SLOPE", "Slope"),
                    ("TRANSPORT_NETWORK", "Transport Network"),
                    ("WATER", "Water"),
                ],
                max_length=50,
            ),
        ),
    ]
