from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import stringcase

from habari.catalog.connectors import (
    DatasourceSummary,
    DatasourceSyncResult,
)
from habari.catalog.models import ExternalContent, Connector, ConnectorQuerySet
from habari.common.models import Base, LocaleField
from .api import Dhis2Client
from ...common.search import SearchResult
from ...common.templatetags.connectors import connector_static_dir


class Dhis2ConnectorQuerySet(ConnectorQuerySet):
    def search(self, query):
        return [
            *Dhis2DataElement.objects.search(query),
            *Dhis2Indicator.objects.search(query),
        ]


class Dhis2Connector(Connector):
    api_url = models.URLField()
    api_username = models.CharField(max_length=200)
    api_password = models.CharField(max_length=200)
    preferred_locale = LocaleField(default="en")

    objects = Dhis2ConnectorQuerySet.as_manager()

    def sync(self):
        """Sync the datasource by querying the DHIS2 API"""

        client = Dhis2Client(
            url=self.api_url, username=self.api_username, password=self.api_password
        )

        # Sync data elements
        data_element_results = Dhis2DataElement.objects.sync_from_dhis2_results(
            self, client.fetch_data_elements()
        )

        # Sync indicator types
        indicator_type_results = Dhis2IndicatorType.objects.sync_from_dhis2_results(
            self, client.fetch_indicator_types()
        )

        # Sync indicators
        indicator_results = Dhis2Indicator.objects.sync_from_dhis2_results(
            self, client.fetch_indicators()
        )

        return data_element_results + indicator_type_results + indicator_results

    def get_content_summary(self):
        return DatasourceSummary(
            data_elements=self.datasource.dhis2dataelement_set.count(),
            indicators=self.datasource.dhis2indicator_set.count(),
        )


class Dhis2DataQuerySet(models.QuerySet):
    @staticmethod
    def _match_name(dhis2_name):
        return f"dhis2_{stringcase.snakecase(dhis2_name)}".replace(
            "dhis2_id", "external_id"
        )

    def _match_reference(self, hexa_name, dhis2_value):
        # No dict? Then return as is
        if not isinstance(dhis2_value, dict):
            return dhis2_value

        # Otherwise, fetch referenced model
        field_info = getattr(self.model, hexa_name)
        related_model = field_info.field.related_model

        try:
            return related_model.objects.get(external_id=dhis2_value["id"])
        except related_model.DoesNotExist:
            return None

    def sync_from_dhis2_results(self, dhis2_connector, results):
        """Iterate over the DEs in the response and create, update or ignore depending on local data"""

        created = 0
        updated = 0
        identical = 0

        for result in results:
            # Build a dict of dhis2 values indexed by hexa field name, and replace reference to other items by
            # their FK
            dhis2_values = {}
            for dhis2_name, dhis2_value in result.get_values(
                dhis2_connector.preferred_locale
            ).items():
                hexa_name = self._match_name(dhis2_name)
                dhis2_values[hexa_name] = self._match_reference(hexa_name, dhis2_value)

            try:
                # Check if the dhis2 data is already in our database and compare values (hexa vs dhis2)
                existing_hexa_item = self.get(external_id=dhis2_values["external_id"])
                existing_hexa_values = {
                    hexa_name: getattr(existing_hexa_item, hexa_name)
                    for hexa_name, _ in dhis2_values
                }
                diff_values = {
                    hexa_name: dhis2_value
                    for hexa_name, dhis2_value in dhis2_values
                    if dhis2_value != existing_hexa_values[hexa_name]
                }

                # Check if we need to actually update the local version
                if len(diff_values) > 0:
                    for hexa_name in diff_values:
                        setattr(
                            existing_hexa_item,
                            hexa_name,
                            diff_values[hexa_name],
                        )
                    updated += 1
                else:
                    identical += 1
            # If we don't have the DE locally, create it
            except ObjectDoesNotExist:
                super().create(**dhis2_values, datasource=dhis2_connector.datasource)
                created += 1

        return DatasourceSyncResult(
            datasource=dhis2_connector.datasource,
            created=created,
            updated=updated,
            identical=identical,
        )


class Dhis2Data(ExternalContent):
    dhis2_name = models.CharField(max_length=200)
    dhis2_short_name = models.CharField(max_length=100, blank=True)
    dhis2_description = models.TextField(blank=True)
    dhis2_external_access = models.BooleanField()
    dhis2_favorite = models.BooleanField()
    dhis2_created = models.DateTimeField()
    dhis2_last_updated = models.DateTimeField()

    objects = Dhis2DataQuerySet.as_manager()

    @property
    def display_name(self):
        return self.dhis2_short_name if self.dhis2_short_name != "" else self.dhis2_name

    class Meta:
        abstract = True
        ordering = ["dhis2_name"]


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


class Dhis2DataElementSearchResult(SearchResult):
    @property
    def result_type(self):
        return "dhis2_data_element"

    @property
    def title(self):
        return self.model.dhis2_name

    @property
    def label(self):
        return _("DHIS2 Data Element")

    @property
    def origin(self):
        return self.model.datasource.name

    @property
    def detail_url(self):
        return reverse(
            "dhis2connector:data_element_detail",
            args=[self.model.datasource.pk, self.model.pk],
        )

    @property
    def updated_at(self):
        return self.model.dhis2_last_updated

    @property
    def symbol(self):
        return f"{settings.STATIC_URL}{connector_static_dir(self.model.datasource)}img/symbol.svg"


class Dhis2DataElementQuerySet(Dhis2DataQuerySet):
    def search(self, query):
        search_vector = SearchVector(
            "external_id",
            "dhis2_name",
            "dhis2_short_name",
            "dhis2_description",
        )
        search_query = SearchQuery(query)
        search_rank = SearchRank(vector=search_vector, query=search_query)
        queryset = (
            self.annotate(rank=search_rank).filter(rank__gt=0).order_by("-rank")[:10]
        )

        return [Dhis2DataElementSearchResult(data_element) for data_element in queryset]


class Dhis2DataElement(Dhis2Data):
    dhis2_code = models.CharField(max_length=100, blank=True)
    dhis2_domain_type = models.CharField(
        choices=Dhis2DomainType.choices, max_length=100
    )
    dhis2_value_type = models.CharField(choices=Dhis2ValueType.choices, max_length=100)
    dhis2_aggregation_type = models.CharField(
        choices=Dhis2AggregationType.choices, max_length=100
    )

    objects = Dhis2DataElementQuerySet.as_manager()

    @property
    def dhis2_domain_type_label(self):
        try:
            return Dhis2DomainType[self.dhis2_domain_type].label
        except KeyError:
            return "Unknown"

    @property
    def dhis2_value_type_label(self):
        try:
            return Dhis2ValueType[self.dhis2_value_type].label
        except KeyError:
            return "Unknown"

    @property
    def dhis2_aggregation_type_label(self):
        try:
            return Dhis2AggregationType[self.dhis2_aggregation_type].label
        except KeyError:
            return "Unknown"


class Dhis2IndicatorSearchResult(SearchResult):
    @property
    def result_type(self):
        return "dhis2_indicator"

    @property
    def title(self):
        return self.model.dhis2_name

    @property
    def label(self):
        return _("DHIS2 Indicator")

    @property
    def origin(self):
        return self.model.datasource.name

    @property
    def detail_url(self):
        return reverse(
            "dhis2connector:indicator_detail",
            args=[self.model.datasource.pk, self.model.pk],
        )

    @property
    def updated_at(self):
        return self.model.dhis2_last_updated

    @property
    def symbol(self):
        return f"{settings.STATIC_URL}{connector_static_dir(self.model.datasource)}img/symbol.svg"


class Dhis2IndicatorQuerySet(Dhis2DataQuerySet):
    def search(self, query):
        search_vector = SearchVector(
            "external_id",
            "dhis2_name",
            "dhis2_short_name",
            "dhis2_description",
        )
        search_query = SearchQuery(query)
        search_rank = SearchRank(vector=search_vector, query=search_query)
        queryset = (
            self.annotate(rank=search_rank).filter(rank__gt=0).order_by("-rank")[:10]
        )

        return [Dhis2IndicatorSearchResult(indicator) for indicator in queryset]


class Dhis2IndicatorType(Dhis2Data):
    dhis2_number = models.BooleanField()
    dhis2_factor = models.IntegerField()


class Dhis2Indicator(Dhis2Data):
    dhis2_code = models.CharField(max_length=100, blank=True)
    dhis2_indicator_type = models.ForeignKey(
        "Dhis2IndicatorType", null=True, on_delete=models.SET_NULL
    )
    dhis2_annualized = models.BooleanField()

    objects = Dhis2IndicatorQuerySet.as_manager()
