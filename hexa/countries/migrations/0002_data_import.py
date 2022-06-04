# Generated by Django 4.0.4 on 2022-05-22 18:35

import json
from pathlib import Path

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.db import migrations


def inject_countries(apps, schema_editor):
    Country = apps.get_model("countries", "Country")
    path_to_file = (
        Path(__file__).resolve().parent / "../data/WHO_ADM0_SIMPLIFIED.geojson"
    )
    raw_countries = json.loads(open(path_to_file).read())["features"]

    for raw_country in raw_countries:
        if raw_country["geometry"]["type"] == "Polygon":
            shape = Polygon(*raw_country["geometry"]["coordinates"])
        elif raw_country["geometry"]["type"] == "MultiPolygon":
            polygons = [
                Polygon(*coords) for coords in raw_country["geometry"]["coordinates"]
            ]
            shape = MultiPolygon(polygons)
        else:
            raise Exception("GeometryType not understood")

        Country.objects.create(
            name=raw_country["properties"]["ADM0_NAME"].title(),
            code=raw_country["properties"]["ISO_2_CODE"],
            alpha3=raw_country["properties"]["ISO_3_CODE"],
            region=raw_country["properties"]["WHO_REGION"],
            default_crs=raw_country["properties"]["DEFAULT_EPSG"],
            simplified_extent=shape,
        )


def truncate_countries(apps, schema_editor):
    Country = apps.get_model("countries", "Country")
    Country.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("countries", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(inject_countries, reverse_code=truncate_countries),
    ]
