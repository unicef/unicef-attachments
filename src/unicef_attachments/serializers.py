import types

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from unicef_restlib.fields import SeparatedReadWriteField
from unicef_restlib.serializers import UserContextSerializerMixin

from unicef_attachments.fields import AttachmentSingleFileField, Base64FileField
from unicef_attachments.models import Attachment, AttachmentLink, FileType
from unicef_attachments.utils import get_attachment_flat_model
from unicef_attachments.validators import SafeFileValidator


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'username',
            'email',
            'is_superuser',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
        )


class BaseAttachmentSerializer(UserContextSerializerMixin, serializers.ModelSerializer):
    uploaded_by = SeparatedReadWriteField(
        write_field=serializers.HiddenField(default=serializers.CurrentUserDefault()),
        read_field=SimpleUserSerializer(label=_('Uploaded By')),
    )

    def _validate_attachment(self, validated_data, instance=None):
        file_attachment = validated_data.get('file', None) or (instance.file if instance else None)
        hyperlink = validated_data.get('hyperlink', None) or (instance.hyperlink if instance else None)

        if bool(file_attachment) == bool(hyperlink):
            raise ValidationError(_('Please provide file or hyperlink.'))

    def create(self, validated_data):
        self._validate_attachment(validated_data)
        return super(BaseAttachmentSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        self._validate_attachment(validated_data, instance=instance)
        return super(BaseAttachmentSerializer, self).update(instance, validated_data)

    class Meta:
        model = Attachment
        fields = [
            'id',
            'file_type',
            'file',
            'hyperlink',
            'created',
            'modified',
            'uploaded_by',
            'filename',
        ]
        extra_kwargs = {
            'created': {
                'label': _('Date Uploaded'),
            },
            'filename': {'read_only': True},
        }


class Base64AttachmentSerializer(BaseAttachmentSerializer):
    file = Base64FileField(required=False, label=_('File Attachment'))
    file_name = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        data = super(Base64AttachmentSerializer, self).validate(attrs)
        file_name = data.pop('file_name', None)
        if 'file' in data and file_name:
            data['file'].name = file_name
        return data

    class Meta(BaseAttachmentSerializer.Meta):
        fields = BaseAttachmentSerializer.Meta.fields + ['file_name', ]


class AttachmentFlatSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="attachment_id")
    file_type_id = serializers.IntegerField(
        source="attachment.file_type.pk",
        read_only=True,
    )

    class Meta:
        model = get_attachment_flat_model()
        fields = "__all__"


class AttachmentLinkSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(
        source="attachment.filename",
        read_only=True,
    )
    url = serializers.CharField(source="attachment.url", read_only=True)
    file_type = serializers.CharField(
        source="attachment.file_type.label",
        read_only=True
    )
    created = serializers.DateTimeField(
        source="attachment.created",
        format="%d %b %Y",
        read_only=True
    )

    class Meta:
        model = AttachmentLink
        fields = (
            "id",
            "attachment",
            "filename",
            "url",
            "file_type",
            "created",
        )


class AttachmentFileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[SafeFileValidator()])
    uploaded_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Attachment
        fields = ["file", "uploaded_by"]


def validate_attachment(cls, data):
    """We expect the attachment pk to be part of the data provided

    The attachment may be empty of content data, in that case
    we are attempting to associate this attachment with the instance,
    which may not exist at the moment.
    If instance does exist, then we can set the content data on the attachment.

    If we do have content data on the attachment, then we expect the instance
    to exist and that it matches that of the attachment.

    We expect the attachment to be updated/saved during the save method,
    so we set the data here, and leave it to be saved later.

    Backward compatibility:
    If we are provided with a valid then we expect it to be valid
    If no value provided, then we assume still working the old way
    """
    value, code = data

    try:
        attachment = Attachment.objects.get(pk=int(value))
    except (ValueError, TypeError):
        raise serializers.ValidationError("Attachment expects an integer")
    except Attachment.DoesNotExist:
        raise serializers.ValidationError("Attachment does not exist")

    file_type, _ = FileType.objects.get_or_create(code=code)
    if attachment.content_object is not None:
        if not cls.instance or attachment.content_object != cls.instance:
            # If content object exists, expect instance to exist
            # as we're not able to re-purpose the attachment
            # Make sure content object matches instance
            raise serializers.ValidationError(
                "Attachment is already associated: {}".format(
                    attachment.content_object
                )
            )

    attachment.file_type = file_type
    attachment.code = code

    return attachment


class AttachmentSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super(AttachmentSerializerMixin, self).__init__(*args, **kwargs)
        self.attachment_list = []
        self.check_attachment_fields()

    def check_attachment_fields(self):
        """If we have a attachment type field

        Then we want to setup validation and save handling
        As attachments are not a field on the object, but rather
        related by way of content type.
        """
        for field_name, field in self.fields.items():
            if isinstance(field, serializers.ListSerializer):
                if hasattr(field.child, "field"):
                    for child_name, child in field.child.field.items():
                        self.handle_attachment_field(child, child_name)
            else:
                self.handle_attachment_field(field, field_name)

    def handle_attachment_field(self, field, field_name):
        if isinstance(field, AttachmentSingleFileField):
            # TODO once attachment flow used throughout
            # we can remove this check on initial data
            # and setting of read only flag, if no matching
            # attachment data
            if not field.read_only and hasattr(self, "initial_data"):
                if field_name in self.initial_data:
                    # TODO remove this once using attachment flow
                    # if we override another field
                    # mark the otherfield as read only
                    if field.override is not None:
                        if field.override in self.fields:
                            self.fields[field.override].read_only = True
                    # ignore values that are None
                    if self.initial_data[field_name] is None or self.initial_data[field_name] == 'None':
                        self.initial_data.pop(field_name)
                    else:
                        setattr(
                            self,
                            "validate_{}".format(field_name),
                            types.MethodType(validate_attachment, self)
                        )
                        self.attachment_list.append(field.source)
                else:
                    setattr(field, "read_only", True)

    def save(self, *args, **kwargs):
        """Attachments are not a relation on the object,

        So we need to remove them from the validated data list
        and then save them individually.
        The attachment objects were setup/created in the validation method
        """
        attachments_to_save = []
        for attachment_attr in self.attachment_list:
            attachments_to_save.append(
                self.validated_data.pop(attachment_attr)
            )
        response = super(AttachmentSerializerMixin, self).save(*args, **kwargs)
        for attachment in attachments_to_save:
            if attachment.content_object is None:
                attachment.content_object = self.instance
            attachment.save()
        return response


class AttachmentPDFSerializer(serializers.ModelSerializer):
    file_type_display = serializers.ReadOnlyField(source='file_type.label')
    created = serializers.DateTimeField(format='%d %b %Y')

    class Meta:
        model = Attachment
        fields = [
            'file_type_display', 'filename', 'url', 'created',
        ]
