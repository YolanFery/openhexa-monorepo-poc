import json
import uuid

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from hexa.catalog.models import (
    CatalogIndex,
    CatalogIndexPermission,
    CatalogIndexType,
)

from hexa.core.models import Permission
from hexa.core.models.cryptography import EncryptedTextField


class DatabaseQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            databasepermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Database(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    hostname = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = EncryptedTextField(max_length=200)
    port = models.IntegerField(default=5432)
    database = models.CharField(max_length=200)

    postfix = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Postgresql Database"
        ordering = ("hostname",)
        unique_together = [("database", "postfix")]

    objects = DatabaseQuerySet.as_manager()

    @property
    def unique_name(self):
        if self.postfix:
            return f"{self.database}{self.postfix}"
        else:
            return self.database

    @property
    def env_name(self):
        slug = self.unique_name.replace("-", "_").upper()
        return f"POSTGRESQL_{slug}"

    @property
    def url(self):
        return f"postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"

    @property
    def safe_url(self):
        return (
            f"postgresql://{self.username}@{self.hostname}:{self.port}/{self.database}"
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index()

    def index(self):
        catalog_index, _ = CatalogIndex.objects.update_or_create(
            defaults={
                "name": self.unique_name,
                "external_name": self.database,
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            index_type=CatalogIndexType.DATASOURCE,
            detail_url=reverse(
                "connector_postgresql:datasource_detail", args=(self.pk,)
            ),
        )

        for permission in self.databasepermission_set.all():
            CatalogIndexPermission.objects.get_or_create(
                catalog_index=catalog_index, team=permission.team
            )

    @property
    def display_name(self):
        return self.unique_name

    def __str__(self):
        return self.display_name


class DatabasePermission(Permission):
    database = models.ForeignKey(
        "connector_postgresql.Database", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [("database", "team")]

    def index_object(self):
        self.database.index()

    def __str__(self):
        return f"Permission for team '{self.team}' on database '{self.database}'"
