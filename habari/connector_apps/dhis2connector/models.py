from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from habari.catalog.models import Content, Datasource
from habari.common.models import Base
from .api import Dhis2Client
from .sync import sync_from_dhis2_results


class Dhis2Instance(Datasource):
    class Meta:
        verbose_name = "DHIS2 instance"

    api_url = models.URLField()
    api_username = models.CharField(max_length=200)
    api_password = models.CharField(max_length=200)

    def sync(self):
        """Sync the datasource by querying the DHIS2 API"""

        client = Dhis2Client(
            url=self.api_url, username=self.api_username, password=self.api_password
        )

        # Sync data elements
        with transaction.atomic():
            data_element_results = sync_from_dhis2_results(
                model_class=Dhis2DataElement,
                dhis2_instance=self,
                results=client.fetch_data_elements(),
            )

            # Sync indicator types
            indicator_type_results = sync_from_dhis2_results(
                model_class=Dhis2IndicatorType,
                dhis2_instance=self,
                results=client.fetch_indicator_types(),
            )

            # Sync indicators
            indicator_results = sync_from_dhis2_results(
                model_class=Dhis2Indicator,
                dhis2_instance=self,
                results=client.fetch_indicators(),
            )

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        return data_element_results + indicator_type_results + indicator_results

    @property
    def content_summary(self):
        if self.last_synced_at is None:
            return ""

        return _(
            "%(data_element_count)s data elements, %(indicator_count)s indicators"
        ) % {
            "data_element_count": self.dhis2dataelement_set.count(),
            "indicator_count": self.dhis2indicator_set.count(),
        }


class Dhis2Content(Content):
    class Meta:
        abstract = True
        ordering = ["dhis2_name"]

    dhis2_id = models.CharField(max_length=200)
    dhis2_instance = models.ForeignKey(
        "Dhis2Instance", null=False, on_delete=models.CASCADE
    )
    dhis2_name = models.CharField(max_length=200)
    dhis2_short_name = models.CharField(max_length=100, blank=True)
    dhis2_description = models.TextField(blank=True)
    dhis2_external_access = models.BooleanField()
    dhis2_favorite = models.BooleanField()
    dhis2_created = models.DateTimeField()
    dhis2_last_updated = models.DateTimeField()

    @property
    def datasource(self):
        return self.dhis2_instance

    def populate_index(self, index):
        index.owner = self.dhis2_instance.owner
        index.name = self.dhis2_name
        index.short_name = self.dhis2_short_name
        index.description = self.dhis2_description
        index.countries = self.dhis2_instance.countries
        index.last_synced_at = self.dhis2_instance.last_synced_at


class Dhis2DomainType(models.TextChoices):
    AGGREGATE = "AGGREGATE", _("Aggregate")
    TRACKER = "TRACKER", _("Tracker")


class Dhis2ValueType(models.TextChoices):
    TEXT = "TEXT", _("Text")
    LONG_TEXT = "LONG_TEXT", _("Long text")
    LETTER = "LETTER", _("Letter")
    PHONE_NUMBER = "PHONE_NUMBER", _("Phone number")
    EMAIL = "EMAIL", _("Email")
    YES_NO = "YES_NO", _("Yes/No")
    YES_ONLY = "YES_ONLY", _("Yes Only")
    DATE = "DATE", _("Date")
    DATE_AND_TIME = "DATE_AND_TIME", _("Date & Time")
    TIME = "TIME", _("Time")
    NUMBER = "NUMBER", _("Number")
    UNIT_INTERVAL = "UNIT_INTERVAL", _("Unit interval")
    PERCENTAGE = "PERCENTAGE", _("Percentage")
    INTEGER = "INTEGER", _("Integer")
    INTEGER_POSITIVE = "INTEGER_POSITIVE", _("Positive Integer")
    INTEGER_NEGATIVE = "INTEGER_NEGATIVE", _("Negative Integer")
    INTEGER_ZERO_OR_POSITIVE = "INTEGER_ZERO_OR_POSITIVE", _("Positive or Zero Integer")
    TRACKER_ASSOCIATE = "TRACKER_ASSOCIATE", _("Tracker Associate")
    USERNAME = "USERNAME", _("Username")
    COORDINATE = "COORDINATE", _("Coordinate")
    ORGANISATION_UNIT = "ORGANISATION_UNIT", _("Organisation Unit")
    AGE = "AGE", _("Age")
    URL = "URL", _("URL")
    FILE = "FILE", _("File")
    IMAGE = "IMAGE", _("Image")


class Dhis2AggregationType(models.TextChoices):
    AVERAGE = "AVERAGE", _("Average")
    AVERAGE_SUM_ORG_UNIT = "AVERAGE_SUM_ORG_UNIT ", _("Average sum for org unit")
    COUNT = "COUNT", _("Count")
    CUSTOM = "CUSTOM", _("Custom")
    DEFAULT = "DEFAULT", _("Default")
    LAST = "LAST", _("Last")
    LAST_AVERAGE_ORG_UNIT = "LAST_AVERAGE_ORG_UNIT", _("Last average for org unit")
    MAX = "MAX", _("Max")
    MIN = "MIN", _("Min")
    NONE = "NONE", _("None")
    STDDEV = "STDDEV", _("Standard Deviation")
    SUM = "SUM", _("Sum")
    VARIANCE = "VARIANCE", _("Variance")


class Dhis2DataElement(Dhis2Content):
    dhis2_code = models.CharField(max_length=100, blank=True)
    dhis2_domain_type = models.CharField(
        choices=Dhis2DomainType.choices, max_length=100
    )
    dhis2_value_type = models.CharField(choices=Dhis2ValueType.choices, max_length=100)
    dhis2_aggregation_type = models.CharField(
        choices=Dhis2AggregationType.choices, max_length=100
    )


class Dhis2IndicatorType(Dhis2Content):
    dhis2_number = models.BooleanField()
    dhis2_factor = models.IntegerField()


class Dhis2Indicator(Dhis2Content):
    dhis2_code = models.CharField(max_length=100, blank=True)
    dhis2_indicator_type = models.ForeignKey(
        "Dhis2IndicatorType", null=True, on_delete=models.SET_NULL
    )
    dhis2_annualized = models.BooleanField()
