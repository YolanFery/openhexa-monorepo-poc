import json
import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from hexa.catalog.models import Content
from hexa.core.models import Base
from hexa.pipelines.models import (
    Environment as BaseEnvironment,
    PipelineIndex,
    PipelineIndexPermission,
    Pipeline,
)


class CredentialsQuerySet(models.QuerySet):
    def get_for_team(self, user):
        # TODO: root credentials concept?
        if user.is_active and user.is_superuser:
            return self.get(team=None)

        if user.team_set.count() == 0:
            raise Credentials.DoesNotExist()

        return self.get(team=user.team_set.first().pk)  # TODO: multiple teams?


class Credentials(Base):
    """This class is a temporary way to store GCP Airflow credentials. This approach is not safe for production,
    as credentials are not encrypted.
    TODO: Store credentials in a secure storage engine like Vault.
    TODO: Handle different kind of credentials (not just OIDC)
    """

    class Meta:
        verbose_name_plural = "Credentials"
        ordering = ("service_account_email",)

    # TODO: unique?
    team = models.ForeignKey(
        "user_management.Team",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="airflow_credential_set",
    )
    service_account_email = models.EmailField()
    service_account_key_data = models.JSONField()
    oidc_target_audience = models.CharField(max_length=200, blank=False)

    objects = CredentialsQuerySet.as_manager()

    def __str__(self):
        return self.service_account_email


class EnvironmentQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            environmentpermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Environment(BaseEnvironment):
    class Meta:
        ordering = ("hexa_name",)

    name = models.CharField(max_length=200)
    url = models.URLField(blank=False)
    api_url = models.URLField()
    api_credentials = models.ForeignKey(
        "Credentials", null=True, on_delete=models.SET_NULL
    )

    objects = EnvironmentQuerySet.as_manager()

    def index(self):
        pipeline_index = PipelineIndex.objects.create_or_update(
            indexed_object=self,
            owner=self.hexa_owner,
            name=self.name,
            countries=self.hexa_countries,
            content_summary=self.content_summary,  # TODO: why?
            last_synced_at=self.hexa_last_synced_at,
            detail_url=reverse("connector_airflow:environment_detail", args=(self.pk,)),
        )

        for permission in self.environmentpermission_set.all():
            PipelineIndexPermission.objects.create(
                catalog_index=pipeline_index, team=permission.team
            )

    @property
    def content_summary(self):
        dag_count = self.dag_set.count()

        return f"{dag_count} DAG{'' if dag_count == 1 else 's'}"

    def __str__(self):
        return self.name


class EnvironmentPermission(Base):
    airflow_environment = models.ForeignKey("Environment", on_delete=models.CASCADE)
    team = models.ForeignKey("user_management.Team", on_delete=models.CASCADE)


class DAGQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            environment__environmentpermission__team__in=[
                t.pk for t in user.team_set.all()
            ]
        )


class DAG(Pipeline):
    class Meta:
        verbose_name = "DAG"
        ordering = ["airflow_id"]

    environment = models.ForeignKey("Environment", on_delete=models.CASCADE)
    airflow_id = models.CharField(max_length=200, blank=False)

    objects = DAGQuerySet.as_manager()

    @property
    def display_name(self):
        return self.airflow_id

    @property
    def last_executed_at(self):
        last_config_run = (
            DAGConfigRun.objects.filter(dag_config__dag=self)
            .order_by("-execution_date")
            .first()
        )

        return last_config_run.execution_date if last_config_run else None

    @property
    def content_summary(self):
        config_count = self.dagconfig_set.count()

        return f"{config_count} DAG configuration{'' if config_count == 1 else 's'}"

    def index(self):
        pass  # TODO: implementation


class DAGConfigQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            dag__environment__environmentpermission__team__in=[
                t.pk for t in user.team_set.all()
            ]
        )


class DAGConfig(Base):
    class Meta:
        verbose_name = "DAG config"

    dag = models.ForeignKey("DAG", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    config_data = models.JSONField(default=dict)

    objects = DAGConfigQuerySet.as_manager()

    @property
    def display_name(self):
        return f"{self.dag.display_name}: {self.name}"

    @property
    def content_summary(self):
        config_count = self.dagconfigrun_set.count()

        return f"{config_count} DAG run{'' if config_count == 1 else 's'}"

    @property
    def last_executed_at(self):
        last_config_run = self.dagconfigrun_set.order_by("-execution_date").first()

        return last_config_run.execution_date if last_config_run else None

    @property
    def last_run_state(self):
        last_config_run = self.dagconfigrun_set.order_by("-execution_date").first()

        return last_config_run.state if last_config_run else None

    def run(self):
        # TODO: move
        # See https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf
        # and https://google-auth.readthedocs.io/en/latest/user-guide.html#identity-tokens
        credentials = service_account.IDTokenCredentials.from_service_account_info(
            self.dag.environment.api_credentials.service_account_key_data,
            target_audience=self.dag.environment.api_credentials.oidc_target_audience,
        )
        session = AuthorizedSession(credentials)
        dag_config_run_id = str(uuid.uuid4())
        response = session.post(
            f"{self.dag.environment.api_url.rstrip('/')}/dags/{self.dag.airflow_id}/dag_runs",
            data=json.dumps(
                {
                    "conf": self.config_data,
                    "run_id": f"openhexa_{dag_config_run_id}",  # TODO: environment
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
        )
        # TODO: handle non-200
        response_data = response.json()

        DAGConfigRun.objects.create(
            id=dag_config_run_id,
            dag_config=self,
            run_id=response_data["run_id"],
            execution_date=response_data["execution_date"],
            message=response_data["message"],
            state=DAGConfigRunState.RUNNING,
            hexa_last_refreshed_at=timezone.now(),
        )

        self.last_run_at = timezone.now()
        self.save()

        return DAGConfigRunResult(self)


class DAGConfigRunResult:
    # TODO: document and move

    def __init__(self, dag_config):
        self.dag_config = dag_config

    def __str__(self):
        return f'The DAG config "{self.dag_config.display_name}" has been run'


class DAGConfigRunQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            dag_config__dag__environment__environmentpermission__team__in=[
                t.pk for t in user.team_set.all()
            ]
        )

    def filter_by_dag(self, dag):
        return self.filter(dag_config__dag=dag)


class DAGConfigRunState(models.TextChoices):
    SUCCESS = "success", _("Success")
    RUNNING = "running", _("Running")
    FAILED = "failed", _("Failed")


class DAGConfigRun(Base):
    dag_config = models.ForeignKey("DAGConfig", on_delete=models.CASCADE)
    run_id = models.CharField(max_length=200, blank=False)
    message = models.TextField()
    execution_date = models.DateTimeField()
    state = models.CharField(
        max_length=200, blank=False, choices=DAGConfigRunState.choices
    )

    hexa_last_refreshed_at = models.DateTimeField(null=True)

    objects = DAGConfigRunQuerySet.as_manager()

    @property
    def display_name(self):
        return f"{self.dag_config.dag.display_name}: {self.dag_config.display_name} ({self.run_id})"

    def refresh(self):
        # TODO: move
        # See https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf
        # and https://google-auth.readthedocs.io/en/latest/user-guide.html#identity-tokens
        credentials = service_account.IDTokenCredentials.from_service_account_info(
            self.dag_config.dag.environment.api_credentials.service_account_key_data,
            target_audience=self.dag_config.dag.environment.api_credentials.oidc_target_audience,
        )
        session = AuthorizedSession(credentials)

        response = session.get(
            f"{self.dag_config.dag.environment.api_url.rstrip('/')}/dags/{self.dag_config.dag.airflow_id}/dag_runs/{self.execution_date.isoformat()}",
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
        )
        # TODO: handle non-200
        response_data = response.json()

        self.hexa_last_refreshed_at = timezone.now()
        self.state = response_data["state"]
        self.save()

    @property
    def finished(self):
        return self.state in ["queued"]

    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "message": self.message,
            "execution_date": date_format(
                self.execution_date, "M d, H:i:s (e)"
            ),  # TODO: helper method
            "hexa_last_refreshed_at": date_format(
                self.hexa_last_refreshed_at, "M d, H:i:s (e)"
            ),
            "state": self.state,
        }

    class Meta:
        ordering = ("-hexa_last_refreshed_at",)