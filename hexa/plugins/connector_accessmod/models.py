from __future__ import annotations

import base64
import enum
import json
import typing

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.db.models import Q
from django.http import HttpRequest
from django_countries.fields import Country, CountryField
from dpq.models import BaseJob
from model_utils.managers import InheritanceManager, InheritanceQuerySet

from hexa.catalog.models import Datasource, Entry
from hexa.core import mimetypes
from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.pipelines.models import Pipeline
from hexa.plugins.connector_airflow import models as airflow_models
from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import Permission, PermissionMode, Team


class ProjectQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user,
            Q(projectpermission__user=user)
            | Q(projectpermission__team__in=Team.objects.filter_for_user(user)),
            return_all_if_superuser=False,
        )


class ProjectManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        name: str,
        country: Country,
        spatial_resolution: int,
        description: str,
        crs: int,
        extent: typing.List,
    ):
        if not principal.has_perm("connector_accessmod.create_project"):
            raise PermissionDenied

        project = self.create(
            name=name,
            country=country,
            spatial_resolution=spatial_resolution,
            crs=crs,
            extent=extent,
            description=description,
            author=principal,
        )
        ProjectPermission.objects.create_if_has_perm(
            principal,
            user=principal,
            project=project,
            mode=PermissionMode.OWNER,
        )

        return project


class Project(Datasource):
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint("name", "author", name="project_unique_name_author")
        ]

    name = models.TextField(verbose_name="project name")
    country = CountryField()
    author = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    description = models.TextField(verbose_name="Project description", blank=True)
    spatial_resolution = models.PositiveIntegerField()
    crs = models.PositiveIntegerField()
    extent = models.JSONField(default=list)
    # FIXME: probably not useful, project can have several DEM
    dem = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )

    objects = ProjectManager.from_queryset(ProjectQuerySet)()

    @property
    def owner(
        self,
    ) -> typing.Optional[typing.Union[User, Team]]:
        try:
            permission = self.projectpermission_set.get(mode=PermissionMode.OWNER)

            return permission.user if permission.user is not None else permission.team
        except ProjectPermission.DoesNotExist:
            return None

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """We override delete() here because we can't control Django CASCADE order. Foreign keys from Analysis to
        Fileset are PROTECTED, which prevents a simple CASCADE delete at the project level."""

        self.analysis_set.all().delete()

        return super().delete(*args, **kwargs)

    @property
    def display_name(self):
        return self.name

    def sync(self):
        pass  # No need to sync, source of truth is OpenHexa

    def get_pipeline_credentials(self):
        pass

    def get_permission_set(self):
        return self.projectpermission_set.all()

    def populate_index(self, index):
        raise NotImplementedError  # Skip indexing for now

    def get_absolute_url(self):
        raise NotImplementedError

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("connector_accessmod.update_project", self):
            raise PermissionDenied

        for key in [
            "name",
            "country",
            "spatial_resolution",
            "crs",
            "extent",
            "dem",
            "description",
        ]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        return self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("connector_accessmod.delete_project", self):
            raise PermissionDenied

        return super().delete()

    def __str__(self):
        return self.name


class ProjectPermissionManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        user: User = None,
        team: Team = None,
        project: Project,
        mode: PermissionMode,
    ):
        if not principal.has_perm(
            "connector_accessmod.create_project_permission", project
        ):
            raise PermissionDenied

        permission = self.create(
            user=user,
            team=team,
            project=project,
            mode=mode,
        )

        return permission


class ProjectPermissionQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user,
            Q(user=user) | Q(team__in=Team.objects.filter_for_user(user)),
            return_all_if_superuser=False,
        )


class ProjectPermission(Permission):
    class Meta(Permission.Meta):
        constraints = [
            models.UniqueConstraint(
                "team",
                "project",
                name="project_unique_team",
                condition=Q(team__isnull=False),
            ),
            models.UniqueConstraint(
                "user",
                "project",
                name="project_unique_user",
                condition=Q(user__isnull=False),
            ),
            models.CheckConstraint(
                check=Q(team__isnull=False) | Q(user__isnull=False),
                name="project_permission_user_or_team_not_null",
            ),
        ]

    project = models.ForeignKey("connector_accessmod.Project", on_delete=models.CASCADE)

    objects = ProjectPermissionManager.from_queryset(ProjectPermissionQuerySet)()

    @property
    def owner(
        self,
    ) -> typing.Union[User, Team]:
        return self.project.owner

    def index_object(self):
        self.project.build_index()

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm(
            "connector_accessmod.update_project_permission", self.project
        ):
            raise PermissionDenied

        for key in ["mode"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])

        return self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm(
            "connector_accessmod.delete_project_permission", self.project
        ):
            raise PermissionDenied

        return super().delete()

    def __str__(self):
        return f"Permission for team '{self.team}' on AM project '{self.project}'"


class FilesetMode(models.TextChoices):
    # File(s) uploaded by the user while using a client app
    USER_INPUT = "USER_INPUT"

    # File(s) will be downloaded by an automatic acquisition pipeline
    AUTOMATIC_ACQUISITION = "AUTOMATIC_ACQUISITION"


class FilesetStatus(models.TextChoices):
    # We need to run the data acquisition first
    TO_ACQUIRE = "TO_ACQUIRE"

    # Pending: fileset incomplete, upload not started or in progress
    PENDING = "PENDING"

    # Upload finished, validation running
    VALIDATING = "VALIDATING"

    # Validation done, outcome valid or invalid
    VALID = "VALID"
    INVALID = "INVALID"


class FilesetQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.filter(project__in=Project.objects.filter_for_user(user)).distinct()


class FilesetManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        *,
        project: Project,
        automatic_acquisition: bool = False,
        **kwargs,
    ):
        if not principal.has_perm("connector_accessmod.create_fileset", project):
            raise PermissionDenied

        mode = (
            FilesetMode.AUTOMATIC_ACQUISITION
            if automatic_acquisition
            else FilesetMode.USER_INPUT
        )
        status = (
            FilesetStatus.TO_ACQUIRE if automatic_acquisition else FilesetStatus.PENDING
        )

        return self.create(
            author=principal,
            project=project,
            mode=mode,
            status=status,
            **kwargs,
        )


class Fileset(Entry):
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                "name", "project", name="fileset_unique_name_project"
            )
        ]

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    name = models.TextField()
    mode = models.CharField(
        max_length=50, choices=FilesetMode.choices, default=FilesetMode.USER_INPUT
    )
    status = models.CharField(
        max_length=50, choices=FilesetStatus.choices, default=FilesetStatus.PENDING
    )
    role = models.ForeignKey("FilesetRole", on_delete=models.PROTECT)
    author = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    metadata = models.JSONField(blank=True, default=dict)

    objects = FilesetManager.from_queryset(FilesetQuerySet)()

    def update_if_has_perm(self, principal: User, *, name: str):
        if not principal.has_perm("connector_accessmod.update_fileset", self):
            raise PermissionDenied

        self.name = name

        return self.save()

    def set_invalid(self, error):
        if self.metadata is None:
            self.metadata = {}
        self.metadata["validation_error"] = error
        self.status = FilesetStatus.INVALID
        self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("connector_accessmod.delete_fileset", self):
            raise PermissionDenied

        return super().delete()

    @property
    def primary_uri(self) -> typing.Optional[str]:
        # FIXME: manage shapefile multiple related file
        if self.file_set.first():
            return self.file_set.first().uri
        else:
            return None

    @property
    def owner(
        self,
    ) -> typing.Union[User, Team]:
        return self.project.owner

    def get_permission_set(self):
        return self.project.get_permission_set()

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError


class FilesetFormat(models.TextChoices):
    VECTOR = "VECTOR"
    RASTER = "RASTER"
    TABULAR = "TABULAR"


class ValidateFilesetJob(BaseJob):
    # queue table to hold validation job from django-postgres-queue
    # Need to redefine this class to specify a custom table name,
    # to avoid conflicts with other queue in the system
    class Meta:
        db_table = "connector_accessmod_validatefilesetjob"


class FilesetRoleCode(models.TextChoices):
    BARRIER = "BARRIER"
    COVERAGE = "COVERAGE"
    DEM = "DEM"
    FRICTION_SURFACE = "FRICTION_SURFACE"
    GEOMETRY = "GEOMETRY"
    HEALTH_FACILITIES = "HEALTH_FACILITIES"
    LAND_COVER = "LAND_COVER"
    POPULATION = "POPULATION"
    TRANSPORT_NETWORK = "TRANSPORT_NETWORK"
    TRAVEL_TIMES = "TRAVEL_TIMES"
    WATER = "WATER"
    STACK = "STACK"


class FilesetRole(Base):
    class Meta:
        ordering = ["code"]

    name = models.TextField()
    code = models.CharField(max_length=50, choices=FilesetRoleCode.choices)
    format = models.CharField(max_length=20, choices=FilesetFormat.choices)


class FileQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.filter(fileset__in=Fileset.objects.filter_for_user(user)).distinct()


class FileManager(models.Manager):
    def create_if_has_perm(
        self, principal: User, *, fileset: Fileset, uri: str, mime_type: str
    ):
        if not principal.has_perm("connector_accessmod.create_file", fileset):
            raise PermissionDenied

        return self.create(fileset=fileset, uri=uri, mime_type=mime_type)


class File(Entry):
    class Meta:
        ordering = ["-created_at"]

    mime_type = models.CharField(
        max_length=255
    )  # According to the spec https://datatracker.ietf.org/doc/html/rfc4288#section-4.2
    uri = models.TextField(unique=True)
    fileset = models.ForeignKey("Fileset", on_delete=models.CASCADE)

    objects = FileManager.from_queryset(FileQuerySet)()

    def get_permission_set(self):
        return self.fileset.get_permission_set()

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    @property
    def name(self):
        return self.uri.split("/")[-1]


class AnalysisStatus(models.TextChoices):
    DRAFT = "DRAFT"
    READY = "READY"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class AnalysisType(str, enum.Enum):
    ACCESSIBILITY = "ACCESSIBILITY"
    GEOGRAPHIC_COVERAGE = "GEOGRAPHIC_COVERAGE"


class AnalysisQuerySet(BaseQuerySet, InheritanceQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user,
            Q(project__projectpermission__user=user)
            | Q(
                project__projectpermission__team__in=Team.objects.filter_for_user(user)
            ),
            return_all_if_superuser=False,
        )


class AnalysisManager(InheritanceManager):
    """Unfortunately, InheritanceManager does not support from_queryset, so we have to subclass it
    and "re-attach" the queryset methods ourselves."""

    def get_queryset(self):
        return AnalysisQuerySet(self.model)

    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.get_queryset().filter_for_user(user)

    def create_if_has_perm(self, principal: User, *, project: Project, **kwargs):
        if not principal.has_perm("connector_accessmod.create_analysis", project):
            raise PermissionDenied

        for key in kwargs:
            if not hasattr(self.model, key):
                raise ValueError(f'Invalid {self.model} attribute "{key}"')

        return self.create(author=principal, project=project, **kwargs)


class Analysis(Pipeline):
    """Base analysis class

    NOTE: This model is impacted by a signal (see signals.py in the current module)
    Whenever a DAGRun linked to an analysis has a new state, the analysis status is likely to change.
    (see also the update_status_from_dag_run_state() method of this class)
    """

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                "name", "project", name="analysis_unique_name_project"
            )
        ]

    DAG_RUN_STATE_MAPPINGS = {
        airflow_models.DAGRunState.QUEUED: AnalysisStatus.QUEUED,
        airflow_models.DAGRunState.RUNNING: AnalysisStatus.RUNNING,
        airflow_models.DAGRunState.SUCCESS: AnalysisStatus.SUCCESS,
        airflow_models.DAGRunState.FAILED: AnalysisStatus.FAILED,
    }
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    author = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=50, choices=AnalysisStatus.choices, default=AnalysisStatus.DRAFT
    )
    name = models.TextField()
    dag_run = models.ForeignKey(
        "connector_airflow.DAGRun",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )

    objects = AnalysisManager()

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("connector_accessmod.update_analysis", self):
            raise PermissionDenied

        for key in kwargs:
            if not hasattr(self, key):
                raise ValueError(f'Invalid {self} attribute "{key}"')
            setattr(self, key, kwargs[key])

        return self.save()

    def run_if_has_perm(
        self,
        principal: User,
        *,
        request: HttpRequest,
        # FIXME: what is this parameters?
        conf: typing.Mapping[str, typing.Any] = None,
        webhook_path: str = None,
    ):
        if not principal.has_perm("connector_accessmod.run_analysis", self):
            raise PermissionDenied

        return self.run(request=request, conf=conf, webhook_path=webhook_path)

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("connector_accessmod.delete_analysis", self):
            raise PermissionDenied

        if self.status in [AnalysisStatus.QUEUED, AnalysisStatus.RUNNING]:
            raise ValueError(f"Cannot delete analyses in {self.status} state")

        return super().delete()

    def get_permission_set(self):
        return self.project.get_permission_set()

    @property
    def owner(
        self,
    ) -> typing.Union[User, Team]:
        return self.project.owner

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        if self.status == AnalysisStatus.DRAFT:
            self.update_status_if_draft()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status in [AnalysisStatus.QUEUED, AnalysisStatus.RUNNING]:
            raise ValueError(f"Cannot delete analyses in {self.status} state")
        return super().delete(*args, **kwargs)

    @transaction.atomic
    def run(
        self,
        *,
        request: HttpRequest,
        # FIXME: what is this parameters?
        conf: typing.Mapping[str, typing.Any] = None,
        webhook_path: str = None,
    ):
        if self.status != AnalysisStatus.READY:
            raise ValueError(f"Cannot run analyses in {self.status} state")

        dag = airflow_models.DAG.objects.get(dag_id=self.dag_id)

        # This is a temporary solution until we figure out storage requirements
        if settings.ACCESSMOD_S3_BUCKET_NAME is None:
            raise ValueError("ACCESSMOD_S3_BUCKET_NAME is not set")
        try:
            bucket = Bucket.objects.get(name=settings.ACCESSMOD_S3_BUCKET_NAME)
        except Bucket.DoesNotExist:
            raise ValueError(
                f"The {settings.ACCESSMOD_S3_BUCKET_NAME} bucket does not exist"
            )

        self.dag_run = dag.run(
            request=request,
            conf=self.build_dag_conf(
                output_dir=f"s3://{bucket.name}/{self.project.id}/{self.id}/"
            ),
            webhook_path=webhook_path,
        )

        self.status = AnalysisStatus.QUEUED
        self.save()

    @property
    def type(self) -> AnalysisType:
        raise NotImplementedError

    @property
    def dag_id(self):
        raise NotImplementedError

    def build_dag_conf(self, output_dir: str):
        raise NotImplementedError

    def update_status_if_draft(self):
        raise NotImplementedError

    def update_status(self, status: AnalysisStatus):
        if self.status in [status, AnalysisStatus.SUCCESS, AnalysisStatus.FAILED]:
            # If no status change or already successful or failed, do nothing
            return
        elif (
            self.status == AnalysisStatus.QUEUED
            and status
            in [AnalysisStatus.RUNNING, AnalysisStatus.SUCCESS, AnalysisStatus.FAILED]
        ) or (
            self.status == AnalysisStatus.RUNNING
            and status in [AnalysisStatus.SUCCESS, AnalysisStatus.FAILED]
        ):
            self.status = status
            self.save()
        else:
            raise ValueError(f"Cannot change status from {self.status} to {status}")

    def update_status_from_dag_run_state(self, state: airflow_models.DAGRunState):
        try:
            new_status_candidate = self.DAG_RUN_STATE_MAPPINGS[state]
            if new_status_candidate != self.status:
                self.update_status(self.DAG_RUN_STATE_MAPPINGS[state])
        except KeyError:
            raise ValueError(f"Cannot map DAGRunState {state}")

    def set_input(self, **kwargs):
        raise NotImplementedError

    def set_outputs(self, **kwargs):
        raise NotImplementedError

    def set_output(
        self,
        *,
        output_key: str,
        output_role_code: FilesetRoleCode,
        output_name: str,
        output_value: str,
    ):
        setattr(
            self,
            output_key,
            Fileset.objects.create(
                project=self.project,
                name=f"{output_name} ({self.name})",
                role=FilesetRole.objects.get(code=output_role_code),
                author=self.author,
            ),
        )
        getattr(self, output_key).file_set.create(
            mime_type=mimetypes.guess_type(output_value)[0], uri=output_value
        )
        self.save()


class AccessibilityAnalysisAlgorithm(models.TextChoices):
    ANISOTROPIC = "ANISOTROPIC"
    ISOTROPIC = "ISOTROPIC"


class AccessibilityAnalysis(Analysis):
    class Meta:
        verbose_name_plural = "Accessibility analyses"

    land_cover = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    dem = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    transport_network = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    water = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    barrier = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    moving_speeds = models.JSONField(blank=True, default=dict)
    health_facilities = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    stack = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    invert_direction = models.BooleanField(default=False)
    max_travel_time = models.IntegerField(default=360)
    stack_priorities = models.JSONField(null=True, blank=True, default=dict)

    water_all_touched = models.BooleanField(default=True)
    algorithm = models.CharField(
        max_length=50,
        choices=AccessibilityAnalysisAlgorithm.choices,
        default=AccessibilityAnalysisAlgorithm.ANISOTROPIC,
    )
    knight_move = models.BooleanField(default=False)

    travel_times = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    friction_surface = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    def update_status_if_draft(self):
        # all of these info must be set & valid
        if (
            not self.name
            or self.health_facilities is None
            or self.health_facilities.status != FilesetStatus.VALID
            or self.dem is None
            or self.dem.status != FilesetStatus.VALID
            or not self.moving_speeds
        ):
            return

        # two mode: 1/ use a stack, 2/ give transport/water/land cover
        if self.stack:
            if self.stack.status != FilesetStatus.VALID:
                # invalid stack -> not ready
                return
        else:
            if (
                self.land_cover is None
                or self.land_cover.status
                not in (FilesetStatus.VALID, FilesetStatus.TO_ACQUIRE)
                or not self.stack_priorities
            ):
                # not enough fileset/invalid filesets for stackless mode
                return

            if self.transport_network is not None:
                if self.transport_network.status not in (
                    FilesetStatus.VALID,
                    FilesetStatus.TO_ACQUIRE,
                ):
                    # transport network used but not in a good state
                    return

            if self.water is not None:
                if self.water.status not in (
                    FilesetStatus.VALID,
                    FilesetStatus.TO_ACQUIRE,
                ):
                    # water used but not in a good state
                    return

        self.status = AnalysisStatus.READY

    @transaction.atomic
    def set_input(
        self,
        input: str,
        uri: str,
        mime_type: str,
        metadata: typing.Optional[typing.Dict[str, typing.Any]],
    ):
        if input not in (
            "land_cover",
            "dem",
            "transport_network",
            "water",
            "health_facilities",
        ):
            raise Exception("invalid input")

        fileset = getattr(self, input)
        if fileset.status != FilesetStatus.TO_ACQUIRE:
            raise Exception("invalid fileset status")

        # add data to that fileset
        File.objects.create(
            mime_type=mime_type,
            uri=uri,
            fileset=fileset,
        )

        # probably the acquisition is valid, use the data worker for
        # metadata extraction
        fileset.status = FilesetStatus.PENDING
        if metadata is not None:
            fileset.metadata.update(metadata)
        fileset.save()
        return fileset

    @transaction.atomic
    def set_outputs(
        self,
        travel_times: str,
        friction_surface: str,
        stack: str = None,
    ):
        self.set_output(
            output_key="travel_times",
            output_role_code=FilesetRoleCode.TRAVEL_TIMES,
            output_name="Travel times",
            output_value=travel_times,
        )
        self.set_output(
            output_key="friction_surface",
            output_role_code=FilesetRoleCode.FRICTION_SURFACE,
            output_name="Friction surface",
            output_value=friction_surface,
        )
        if stack is not None:
            self.set_output(
                output_key="stack",
                output_role_code=FilesetRoleCode.STACK,
                output_name="Stack",
                output_value=stack,
            )

    @property
    def type(self) -> AnalysisType:
        return AnalysisType.ACCESSIBILITY

    @property
    def dag_id(self):
        return "am_accessibility_full"

    def build_dag_conf(self, output_dir: str):
        # if build_dag_conf -> status is ready. so assume:
        # name, land_cover, transport_network, water, health_facilities, dem
        # as non null

        # force output_dir to end with a "/"
        if not output_dir.endswith("/"):
            output_dir += "/"

        am_conf = {
            "output_dir": output_dir,
            "algorithm": self.algorithm,
            "max_travel_time": self.max_travel_time,
            "knight_move": self.knight_move,
            "invert_direction": self.invert_direction,
            "moving_speeds": self.moving_speeds,
            "extent": self.project.extent,
            "crs": self.project.crs,
            "country": {
                "name": self.project.country.name,
                "iso-a2": self.project.country.code,
                "iso-a3": self.project.country.alpha3,
            },
            "spatial_resolution": self.project.spatial_resolution,
            # Overwrite existing files -> easier to debug (temporary)
            "overwrite": True,
        }

        if self.dem.status == FilesetStatus.TO_ACQUIRE:
            am_conf["dem"] = {
                "auto": True,
                "name": self.dem.name,
                "path": output_dir + f"{str(self.dem.id)}_dem.tif",
            }
        else:
            am_conf["dem"] = {
                "auto": False,
                "name": self.dem.name,
                "path": self.dem.primary_uri,
            }

        if self.health_facilities.status == FilesetStatus.TO_ACQUIRE:
            am_conf["health_facilities"] = {
                "auto": True,
                "amenity": None,
                "name": self.health_facilities.name,
                "path": output_dir
                + f"{str(self.health_facilities.id)}_facilities.gpkg",
            }
        else:
            am_conf["health_facilities"] = {
                "auto": False,
                "name": self.health_facilities.name,
                "path": self.health_facilities.primary_uri,
                # FIXME: filter by amenity todo
            }

        if self.land_cover.status == FilesetStatus.TO_ACQUIRE:
            am_conf["land_cover"] = {
                "auto": True,
                "name": self.land_cover.name,
                "path": output_dir + f"{str(self.land_cover.id)}_land_cover.tif",
                "labels": self.land_cover.metadata.get("labels", None),
                # FIXME: you can use 2015 -> 2019 as year for data source
                "year": 2019,
            }
        else:
            am_conf["land_cover"] = {
                "auto": False,
                "name": self.land_cover.name,
                "path": self.land_cover.primary_uri,
                "labels": self.land_cover.metadata.get("labels", None),
            }

        if self.transport_network.status == FilesetStatus.TO_ACQUIRE:
            am_conf["transport_network"] = {
                "auto": True,
                "name": self.transport_network.name,
                "path": output_dir + f"{str(self.transport_network.id)}_transport.gpkg",
                "category_column": self.transport_network.metadata.get(
                    "category_column", None
                ),
            }
        else:
            am_conf["transport_network"] = {
                "auto": False,
                "name": self.transport_network.name,
                "path": self.transport_network.primary_uri,
                "category_column": self.transport_network.metadata.get(
                    "category_column", None
                ),
            }

        if self.water.status == FilesetStatus.TO_ACQUIRE:
            am_conf["water"] = {
                "auto": True,
                "name": self.water.name,
                "path": output_dir + f"{str(self.water.id)}_water.gpkg",
                "all_touched": self.water_all_touched,
            }
        else:
            am_conf["water"] = {
                "auto": False,
                "name": self.water.name,
                "path": self.water.primary_uri,
                "all_touched": self.water_all_touched,
            }

        # Do we have a stack to use or do we need to build it?
        if self.stack:
            am_conf["stack"] = {
                "name": self.stack.name,
                "path": self.stack.primary_uri,
                "labels": self.stack.metadata.get("labels", None),
            }
        else:
            am_conf["stack"] = None
            am_conf["priorities"] = self.stack_priorities
            if self.barrier:
                am_conf["barriers"] = [
                    {
                        "name": self.barrier.name,
                        "path": self.barrier.primary_uri,
                        "labels": self.barrier.metadata.get("labels", None),
                        # "all_touched": #FIXME: Not sure if we need to add this
                    }
                ]

        dag_conf = {
            # flag interpreted by airflow for starting acquisition pipelines
            "acquisition_healthsites": self.health_facilities.status
            == FilesetStatus.TO_ACQUIRE,
            "acquisition_copernicus": self.land_cover.status
            == FilesetStatus.TO_ACQUIRE,
            "acquisition_osm": (
                self.transport_network.status == FilesetStatus.TO_ACQUIRE
                or self.water.status == FilesetStatus.TO_ACQUIRE
            ),
            "acquisition_srtm": self.dem.status == FilesetStatus.TO_ACQUIRE,
            # Overwrite and output_dir repeated: for create report, which
            # doesnt parse am_config
            "overwrite": True,
            "output_dir": output_dir,
            # config for accessibility pipeline
            "am_config": base64.b64encode(json.dumps(am_conf).encode()).decode(),
        }

        return dag_conf


class GeographicCoverageAnalysis(Analysis):
    population = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    friction_surface = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    dem = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    health_facilities = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    anisotropic = models.BooleanField(default=True)
    max_travel_time = models.IntegerField(null=True, default=360)
    hf_processing_order = models.CharField(max_length=100)

    geographic_coverage = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    catchment_areas = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    def update_status_if_draft(self):
        if all(
            value is not None
            for value in [
                getattr(self, field)
                for field in [
                    "name",
                    "population",
                    "friction_surface",
                    "dem",
                    "health_facilities",
                    "hf_processing_order",
                ]
            ]
        ):
            self.status = AnalysisStatus.READY

    @transaction.atomic
    def set_outputs(self, geographic_coverage: str, catchment_areas: str):
        self.set_output(
            output_key="geographic_coverage",
            output_role_code=FilesetRoleCode.COVERAGE,
            output_name="Geographic coverage",
            output_value=geographic_coverage,
        )

    @property
    def type(self) -> AnalysisType:
        return AnalysisType.GEOGRAPHIC_COVERAGE

    @property
    def dag_id(self):
        return "am_geographic_coverage"

    def build_dag_conf(self, output_dir: str):
        raise NotImplementedError
