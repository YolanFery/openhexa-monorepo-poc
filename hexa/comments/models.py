from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from hexa.core.models import Base


class CommentQuerySet(models.QuerySet):
    def for_content(self, content):
        return self.filter(object=content)


class Comment(Base):
    class Meta:
        ordering = ["-created_at"]

    user = models.ForeignKey("user_management.User", on_delete=models.CASCADE)
    index = models.ForeignKey(
        "catalog.Index", on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()

    objects = CommentQuerySet.as_manager()
