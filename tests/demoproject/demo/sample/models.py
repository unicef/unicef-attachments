from django.db import models
from unicef_djangolib.fields import CodedGenericRelation

from unicef_attachments.models import Attachment


class Author(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    image = models.FileField(null=True, blank=True)
    profile_image = CodedGenericRelation(
        Attachment,
        verbose_name='Profile Image',
        code='author_profile_image',
        blank=True,
        null=True,
    )

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Book(models.Model):
    author = models.ForeignKey(
        Author,
        related_name="books",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class AttachmentFlatOverride(models.Model):
    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
    )
    object_link = models.URLField(blank=True, verbose_name="Object Link")
