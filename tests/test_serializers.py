import os

import pytest
from rest_framework.exceptions import ValidationError
from tests.factories import UserFactory

from unicef_attachments.serializers import Base64AttachmentSerializer

pytestmark = pytest.mark.django_db


def test_invalid(file_type):
    invalid_serializer = Base64AttachmentSerializer(data={
        'file_type': file_type.pk,
    }, context={'user': UserFactory()})

    assert invalid_serializer.is_valid()
    # file and hyperlink validation were moved to save in fact
    with pytest.raises(ValidationError) as ex:
        invalid_serializer.save()

    assert 'Please provide file or hyperlink.' in ex.value.detail


def test_valid(file_type, base64_file):
    valid_serializer = Base64AttachmentSerializer(data={
        'file': base64_file,
        'file_name': "simple_file.txt",
        'file_type': file_type.pk,
    }, context={'user': UserFactory()})
    assert valid_serializer.is_valid()

    attachment_instance = valid_serializer.save(content_object=file_type)

    assert os.path.splitext(
        os.path.split(attachment_instance.file.url)[-1]
    )[0].startswith(
        os.path.splitext("simple_file.txt")[0]
    )
