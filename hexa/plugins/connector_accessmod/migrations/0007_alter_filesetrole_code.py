# Generated by Django 4.0.2 on 2022-02-16 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_accessmod", "0006_fileset_role_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filesetrole",
            name="code",
            field=models.CharField(
                choices=[
                    ("LAND_COVER", "Land Cover"),
                    ("DEM", "Dem"),
                    ("TRANSPORT_NETWORK", "Transport Network"),
                    ("SLOPE", "Slope"),
                    ("WATER", "Water"),
                    ("BARRIER", "Barrier"),
                    ("MOVING_SPEEDS", "Moving Speeds"),
                    ("HEALTH_FACILITIES", "Health Facilities"),
                ],
                max_length=50,
            ),
        ),
    ]
