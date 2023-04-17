import base64

from rest_framework import serializers

import pytest

from tests.factories import AttachmentFactory, AttachmentFileTypeFactory
from unicef_attachments.fields import AttachmentSingleFileField, Base64FileField
from unicef_attachments.models import Attachment

from demo.sample.serializers import AuthorFileTypeSerializer

pytestmark = pytest.mark.django_db


def test_base64_file_field_valid():
    file_content = "these are the file contents!".encode("utf-8")
    valid_base64_file = "data:text/plain;base64,{}".format(base64.b64encode(file_content))
    value = Base64FileField().to_internal_value(valid_base64_file)
    assert value is not None


def test_base64_file_field_invalid():
    with pytest.raises(serializers.ValidationError):
        Base64FileField().to_internal_value(42)


def test_base64_file_field_corrupted():
    file_content = "these are the file contents!".encode("utf-8")
    corrupted_base64_file = "data;base64,{}".format(base64.b64encode(file_content))
    with pytest.raises(serializers.ValidationError):
        Base64FileField().to_internal_value(corrupted_base64_file)


def test_model_choice_file_field_valid_serializer():
    file_type = AttachmentFileTypeFactory(code="author_profile_image")
    serializer = AuthorFileTypeSerializer(
        data={
            "file_type": file_type.pk,
            "first_name": "Joe",
            "last_name": "Soap",
        }
    )
    assert serializer.is_valid()


def test_model_choice_file_field_invalid_serializer():
    file_type = AttachmentFileTypeFactory(code="wrong")
    serializer = AuthorFileTypeSerializer(
        data={
            "file_type": file_type.pk,
            "first_name": "Joe",
            "last_name": "Soap",
        }
    )
    assert not serializer.is_valid()
    assert "file_type" in serializer.errors
    s = 'Invalid option "{pk_value}" - option is not available.'.format(pk_value=file_type.pk)
    assert s in serializer.errors["file_type"]


def test_attachment_single_file_field_no_attribute(file_type):
    field = AttachmentSingleFileField(source="wrong")
    assert field.get_attribute(file_type) is None


def test_attachment_single_file_field_no_attachment(file_type):
    file_type.attachment = Attachment.objects.filter(code=file_type.code)
    field = AttachmentSingleFileField(source="attachment")
    assert field.get_attribute(file_type) is None


def test_attachment_single_file_field_attachment(file_type, upload_file):
    file_type.attachment = Attachment.objects.filter(code=file_type.code)
    field = AttachmentSingleFileField(source="attachment")
    attachment = AttachmentFactory(
        file_type=file_type,
        content_object=file_type,
        code=file_type.code,
        file=upload_file,
    )
    assert field.get_attribute(file_type) == attachment.file


def test_attachment_single_file_field_last_attachment(file_type, upload_file):
    file_type.attachment = Attachment.objects.filter(code=file_type.code)
    field = AttachmentSingleFileField(source="attachment")
    AttachmentFactory(
        file_type=file_type,
        content_object=file_type,
        code=file_type.code,
    )
    attachment = AttachmentFactory(
        file_type=file_type,
        content_object=file_type,
        code=file_type.code,
        file=upload_file,
    )
    assert field.get_attribute(file_type) == attachment.file
