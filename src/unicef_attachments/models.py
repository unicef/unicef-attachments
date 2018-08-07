import os
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel
from ordered_model.models import OrderedModel

from unicef_attachments.utils import filepath_prefix, get_denormalize_func


def generate_file_path(attachment, filename):
    if attachment.content_type:
        app = attachment.content_type.app_label
        model_name = attachment.content_type.model
    else:
        app = "unknown"
        model_name = "tmp"
    obj_pk = attachment.object_id

    file_path = [
        filepath_prefix,
        "files",
        app,
        slugify(model_name),
        attachment.code,
        obj_pk,
    ]

    file_path.append(os.path.split(filename)[-1])
    # strip all '/'
    file_path = [str(x).strip("/") for x in file_path if x]
    return '/'.join(file_path)


class FileType(OrderedModel, models.Model):
    name = models.CharField(max_length=64, verbose_name=_('Name'))
    label = models.CharField(max_length=64, verbose_name=_('Label'))
    code = models.CharField(max_length=64, default="", verbose_name=_('Code'))

    def __str__(self):
        return self.label

    class Meta:
        unique_together = ("name", "code", )
        ordering = ('code', 'order')


class Attachment(TimeStampedModel, models.Model):
    file_type = models.ForeignKey(
        FileType,
        verbose_name=_('Document Type'),
        null=True,
        on_delete=models.CASCADE,
    )
    file = models.FileField(
        upload_to=generate_file_path,
        blank=True,
        null=True,
        verbose_name=_('File Attachment'),
        max_length=1024,
    )
    hyperlink = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_('Hyperlink')
    )
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        verbose_name=_('Content Type'),
        on_delete=models.CASCADE,
    )
    object_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Object ID')
    )
    content_object = GenericForeignKey()
    code = models.CharField(max_length=64, blank=True, verbose_name=_('Code'))
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Uploaded By"),
        related_name='attachments',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['id', ]

    def __str__(self):
        return str(self.file)

    def clean(self):
        super(Attachment, self).clean()
        if bool(self.file) == bool(self.hyperlink):
            raise ValidationError(_('Please provide file or hyperlink.'))

    @property
    def url(self):
        if self.file:
            return self.file.url
        else:
            return self.hyperlink

    @property
    def filename(self):
        return os.path.basename(
            self.file.name if self.file else urlsplit(self.hyperlink).path
        )

    @property
    def file_link(self):
        return reverse("attachments:file", args=[self.pk])

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)

        # check if we want to denormalize attachment data
        denormalize_func = get_denormalize_func()
        if denormalize_func is not None:
            denormalize_func(self)


class AttachmentLink(models.Model):
    attachment = models.ForeignKey(
        Attachment,
        related_name="links",
        on_delete=models.CASCADE,
    )
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        verbose_name=_('Content Type'),
        on_delete=models.CASCADE,
    )
    object_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Object ID')
    )
    content_object = GenericForeignKey()

    def __str__(self):
        return "{} link".format(self.attachment)


class AttachmentFlat(models.Model):
    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
    )
    object_link = models.URLField(blank=True, verbose_name=_("Object Link"))
    file_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('File Type')
    )
    file_link = models.CharField(
        max_length=1024,
        blank=True,
        verbose_name=_('File Link')
    )
    filename = models.CharField(
        max_length=1024,
        blank=True,
        verbose_name=_('File Name')
    )
    uploaded_by = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Uploaded by')
    )
    created = models.CharField(max_length=50, verbose_name=_('Created'))

    def __str__(self):
        return str(self.attachment)
