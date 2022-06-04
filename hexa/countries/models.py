from django.contrib.gis.db import models
from django_countries.fields import Country as DjangoCountry

from hexa.core.models import Base

WHO_REGION_NAMES = {
    "AMRO": "Region of the Americas",
    "AFRO": "African Region",
    "EMRO": "Eastern Mediterranean Region",
    "EURO": "European Region",
    "WPRO": "Western Pacific Region",
    "SEARO": "South-East Asian Region",
}


class WHORegion(models.TextChoices):
    AMRO = "AMRO"
    AFRO = "AFRO"
    EMRO = "EMRO"
    EURO = "EURO"
    WPRO = "WPRO"
    SEARO = "SEARO"


class Country(Base):
    name = models.TextField()
    code = models.CharField(max_length=2)
    alpha3 = models.CharField(max_length=3)

    # WHO Info
    region = models.CharField(max_length=50, choices=WHORegion.choices)
    default_crs = models.IntegerField()
    simplified_extent = models.GeometryField()

    def get_who_info(self):
        return {
            "region": {
                "code": self.region,
                "name": WHO_REGION_NAMES[self.region],
            },
            "default_crs": self.default_crs,
            "simplified_extent": [[x, y] for x, y in self.simplified_extent.tuple[0]],
        }

    def flag(self):
        return DjangoCountry(self.code).flag
