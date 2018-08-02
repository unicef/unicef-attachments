import os

import pytest
from demo.sample.serializers import AuthorOverrideSerializer, AuthorSerializer
from rest_framework.exceptions import ValidationError
from tests.factories import AttachmentFactory, AttachmentFileTypeFactory, UserFactory

from unicef_attachments.models import Attachment
from unicef_attachments.serializers import Base64AttachmentSerializer

pytestmark = pytest.mark.django_db


def test_base64_create_invalid(file_type):
    serializer = Base64AttachmentSerializer(data={
        'file_type': file_type.pk,
    }, context={'user': UserFactory()})

    assert serializer.is_valid()
    # file and hyperlink validation were moved to save in fact
    with pytest.raises(ValidationError) as ex:
        serializer.save()

    assert 'Please provide file or hyperlink.' in ex.value.detail


def test_base64_create_valid(file_type, base64_file):
    serializer = Base64AttachmentSerializer(data={
        'file': base64_file,
        'file_name': "simple_file.txt",
        'file_type': file_type.pk,
    }, context={'user': UserFactory()})
    assert serializer.is_valid()

    attachment_instance = serializer.save(content_object=file_type)

    assert os.path.splitext(
        os.path.split(attachment_instance.file.url)[-1]
    )[0].startswith(
        os.path.splitext("simple_file.txt")[0]
    )


def test_base64_update_valid(file_type, attachment, base64_file):
    serializer = Base64AttachmentSerializer(attachment, data={
        'file': base64_file,
        'file_name': "simple_file.txt",
        'file_type': file_type.pk,
    }, context={'user': UserFactory()})
    assert serializer.is_valid()

    attachment_instance = serializer.save(content_object=file_type)

    assert attachment_instance.pk == attachment.pk
    assert os.path.splitext(
        os.path.split(attachment_instance.file.url)[-1]
    )[0].startswith(
        os.path.splitext("simple_file.txt")[0]
    )


def test_attachment_serializer_invalid_not_integer(attachment_empty):
    file_type = AttachmentFileTypeFactory(code="author_profile_image")
    assert not attachment_empty.code
    assert not attachment_empty.file_type
    serializer = AuthorSerializer(data={
        "first_name": "Joe",
        "last_name": "Soap",
        "profile_image": "wrong",
    })
    assert not serializer.is_valid()
    assert serializer.errors == {
        "profile_image": ["Attachment expects an integer"]
    }


def test_attachment_serializer_invalid_attachment(attachment_empty):
    file_type = AttachmentFileTypeFactory(code="author_profile_image")
    assert not attachment_empty.code
    assert not attachment_empty.file_type
    serializer = AuthorSerializer(data={
        "first_name": "Joe",
        "last_name": "Soap",
        "profile_image": 404,
    })
    assert not serializer.is_valid()
    assert serializer.errors == {
        "profile_image": ["Attachment does not exist"]
    }


def test_attachment_serializer_invalid_associated(attachment):
    file_type = AttachmentFileTypeFactory(code="author_profile_image")
    assert attachment.file_type != file_type
    serializer = AuthorSerializer(data={
        "first_name": "Joe",
        "last_name": "Soap",
        "profile_image": attachment.pk
    })
    assert not serializer.is_valid()
    assert serializer.errors == {
        "profile_image": ["Attachment is already associated: {}".format(
            attachment.content_object
        )]
    }


def test_attachment_serializer_save(attachment_empty):
    file_type = AttachmentFileTypeFactory(code="author_profile_image")
    assert not attachment_empty.code
    assert not attachment_empty.file_type
    serializer = AuthorSerializer(data={
        "first_name": "Joe",
        "last_name": "Soap",
        "profile_image": attachment_empty.pk
    })
    assert serializer.is_valid()
    serializer.save()

    attachment = Attachment.objects.get(pk=attachment_empty.pk)
    assert attachment.code
    assert attachment.file_type == file_type


def test_attachment_serializer_update(author):
    file_type = AttachmentFileTypeFactory(code="author_profile_image")
    attachment = AttachmentFactory(
        content_object=author,
        file_type=file_type,
        code=file_type.code,
        file="test.pdf",
    )
    serializer = AuthorSerializer(author, data={
        "first_name": "Joe",
        "last_name": "Soap",
        "profile_image": attachment.pk
    })
    assert serializer.is_valid()
    serializer.save()

    attachment_updated = Attachment.objects.get(pk=attachment.pk)
    assert attachment_updated.content_object == attachment.content_object
    assert attachment_updated.code == attachment.code
    assert attachment_updated.file_type == attachment.file_type


def test_attachment_serializer_no_attachment(attachment_empty):
    assert not attachment_empty.code
    assert not attachment_empty.file_type
    serializer = AuthorSerializer(data={
        "first_name": "Joe",
        "last_name": "Soap",
    })
    assert serializer.is_valid()
    serializer.save()

    attachment = Attachment.objects.get(pk=attachment_empty.pk)
    assert not attachment.code
    assert not attachment.file_type


def test_attachment_serializer_override(attachment_empty):
    file_type = AttachmentFileTypeFactory(code="author_profile_image")
    assert not attachment_empty.code
    assert not attachment_empty.file_type
    serializer = AuthorOverrideSerializer(data={
        "first_name": "Joe",
        "last_name": "Soap",
        "profile_image": attachment_empty.pk
    })
    assert serializer.is_valid()
    serializer.save()
    assert serializer.fields["image"].read_only

    attachment = Attachment.objects.get(pk=attachment_empty.pk)
    assert attachment.code
    assert attachment.file_type == file_type
