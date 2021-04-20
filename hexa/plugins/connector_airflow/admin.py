from django.contrib import admin
from .models import (
    Environment,
    Credentials,
    EnvironmentPermission,
    DAG,
)


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("service_account_email", "oidc_target_audience", "team")
    search_fields = ("service_account_email",)


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url",
    )
    search_fields = ("name",)


@admin.register(EnvironmentPermission)
class EnvironmentPermissionAdmin(admin.ModelAdmin):
    list_display = ("airflow_environment", "team")


@admin.register(DAG)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ("dag_id",)
    search_fields = ("dag_id",)
