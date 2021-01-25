from django.contrib import admin
from .models import (
    Organization,
    Dhis2Connection,
    Datasource,
    Dhis2Area,
    Dhis2Theme,
    Dhis2DataElement,
    Dhis2Indicator,
)


def country_list(obj):
    return ",".join(country.alpha3 for country in obj.countries)


country_list.short_description = "Countries"


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("display_name", "organization_type", country_list)


class Dhis2ConnectionInlineAdmin(admin.TabularInline):
    model = Dhis2Connection


@admin.register(Datasource)
class DatasourceAdmin(admin.ModelAdmin):
    list_display = ("display_name", "datasource_type", "owner", "public", country_list)
    inlines = [
        Dhis2ConnectionInlineAdmin,
    ]


@admin.register(Dhis2Area)
class Dhis2AreaAdmin(admin.ModelAdmin):
    list_display = ("display_name",)


@admin.register(Dhis2Theme)
class Dhis2ThemeAdmin(admin.ModelAdmin):
    list_display = ("display_name",)


@admin.register(Dhis2DataElement)
class Dhis2DataElementAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "owner",
        "source",
        "dhis2_id",
        "dhis2_code",
        "dhis2_domain_type",
        "dhis2_value_type",
        "dhis2_aggregation_type",
    )
    list_filter = ("source__name",)
    search_fields = ["name", "short_name", "dhis2_id", "dhis2_code"]


@admin.register(Dhis2Indicator)
class Dhis2IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "owner",
        "source",
        "dhis2_id",
        "dhis2_indicator_type",
    )
