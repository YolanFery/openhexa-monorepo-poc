from django.contrib import admin
from .models import (
    Instance,
    DataElement,
    Indicator,
    IndicatorType,
    InstancePermission,
)


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "dhis2_api_url", "last_synced_at")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(DataElement)
class DataElementAdmin(admin.ModelAdmin):
    list_display = (
        "instance",
        "display_name",
        "dhis2_id",
        "dhis2_code",
        "dhis2_domain_type",
        "dhis2_value_type",
        "dhis2_aggregation_type",
    )
    list_filter = ("instance__name",)
    search_fields = [
        "name",
        "short_name",
        "dhis2_name",
        "dhis2_short_name",
        "dhis2_id",
        "dhis2_code",
    ]


@admin.register(IndicatorType)
class IndicatorTypeAdmin(admin.ModelAdmin):
    list_display = (
        "dhis2_id",
        "name",
        "dhis2_number",
        "dhis2_factor",
    )


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "instance",
        "display_name",
        "dhis2_id",
        "dhis2_indicator_type",
    )
    list_filter = ("instance__name",)
    search_fields = [
        "name",
        "dhis2_name",
        "short_name",
        "dhis2_short_name",
        "dhis2_id",
        "dhis2_code",
    ]


@admin.register(InstancePermission)
class InstancePermissionAdmin(admin.ModelAdmin):
    list_display = ("instance", "team")
