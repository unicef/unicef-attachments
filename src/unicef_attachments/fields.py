import base64
import mimetypes
import uuid

from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from unicef_restlib.fields import ModelChoiceField

from unicef_attachments.utils import get_client_ip


class FileTypeModelChoiceField(ModelChoiceField):
    def get_choice(self, obj):
        return obj.pk, obj.label


class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError(_("Incorrect base64 format."))

        try:
            mime, encoded_data = data.replace("data:", "", 1).split(";base64,")
            extension = mimetypes.guess_extension(mime)
            content_file = ContentFile(base64.b64decode(encoded_data), name=str(uuid.uuid4()) + extension)

        except (ValueError, TypeError):
            raise serializers.ValidationError(_("Incorrect base64 format."))

        return content_file


class AttachmentSingleFileField(serializers.Field):
    override = None

    def __init__(self, *args, **kwargs):
        if "override" in kwargs:
            self.override = kwargs.pop("override")
        super().__init__(*args, **kwargs)

    def get_attachment(self, instance):
        if hasattr(instance, self.source):
            attachment = getattr(instance, self.source)
            if attachment and attachment.last():
                return attachment.last()
        return None

    def get_attribute(self, instance):
        attachment = self.get_attachment(instance)
        return attachment.file if attachment is not None else None

    def to_representation(self, value):
        if not value:
            return None

        if not getattr(value, "url", None):
            return None

        url = value.url
        request = self.context.get("request", None)
        if request is not None:
            return request.build_absolute_uri(url)
        return url

    def to_internal_value(self, data):
        """This data is passed to the validation method

        So we package in the code value, as that is needed
        during validation
        """
        attachment = getattr(self.parent.Meta.model, self.source)
        return data, attachment.field.code


class CurrentIPDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return get_client_ip(serializer_field.context["request"])

    def __repr__(self):
        return "%s()" % self.__class__.__name__
