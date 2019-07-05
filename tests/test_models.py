import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from tests.factories import AttachmentFactory, AttachmentFileTypeFactory

from unicef_attachments import models

pytestmark = pytest.mark.django_db


def test_generate_file_path(author):
    attachment = AttachmentFactory(
        content_object=author,
        code="author-image",
    )
    file_path = models.generate_file_path(attachment, "test.pdf")
    assert file_path == "/".join([
        "files",
        "sample",
        "author",
        attachment.code,
        str(author.pk),
        "test.pdf"
    ])


def test_generate_file_path_no_content_type():
    attachment = AttachmentFactory()
    file_path = models.generate_file_path(attachment, "test.pdf")
    assert file_path == "/".join([
        "files",
        "unknown",
        "tmp",
        "test.pdf"
    ])


def test_file_type_str():
    instance = AttachmentFileTypeFactory(label='xyz')
    assert u'xyz' in str(instance)

    instance = AttachmentFileTypeFactory(label='R\xe4dda Barnen')
    assert 'R\xe4dda Barnen' in str(instance)


def test_attachment_str(author):
    instance = AttachmentFactory(
        file=SimpleUploadedFile(
            'simple_file.txt',
            b'these are the file contents!'
        ),
        content_object=author
    )
    assert 'simple_file' in str(instance)

    instance = AttachmentFactory(
        file=SimpleUploadedFile(
            'simple_file.txt',
            u'R\xe4dda Barnen'.encode('utf-8')
        ),
        content_object=author
    )
    assert 'simple_file' in str(instance)


def test_attachment_filename(author):
    instance = AttachmentFactory(file="test.pdf", content_object=author)
    assert instance.filename == "test.pdf"


def test_attachment_filename_hyperlink(author):
    instance = AttachmentFactory(
        hyperlink="http://example.com/test_file.txt",
        content_object=author
    )
    assert instance.filename == "test_file.txt"


def test_attachment_valid_file(author):
    valid_file_attachment = AttachmentFactory(
        # Note: file content is intended to be a byte-string here.
        file=SimpleUploadedFile(
            'simple_file.txt',
            b'these are the file contents!'
        ),
        content_object=author
    )
    valid_file_attachment.clean()
    assert valid_file_attachment.file is not None
    assert valid_file_attachment.url == valid_file_attachment.file.url


def test_attachment_valid_hyperlink(author):
    valid_hyperlink_attachment = AttachmentFactory(
        hyperlink='http://example.com/test_file.txt',
        content_object=author
    )
    valid_hyperlink_attachment.clean()
    assert valid_hyperlink_attachment.hyperlink is not None
    assert valid_hyperlink_attachment.url == valid_hyperlink_attachment.hyperlink


def test_attachment_invalid(author):
    invalid_attachment = AttachmentFactory(content_object=author)
    with pytest.raises(ValidationError):
        invalid_attachment.clean()


def test_attachment_flat_str(author):
    attachment = AttachmentFactory(
        file=SimpleUploadedFile(
            'simple_file.txt',
            u'R\xe4dda Barnen'.encode('utf-8')
        ),
        content_object=author
    )
    flat_qs = models.AttachmentFlat.objects.filter(attachment=attachment)
    assert flat_qs.exists()
    flat = flat_qs.first()
    assert str(flat) == str(attachment.file)


def test_attachment_list_str(attachment_link):
    assert str(attachment_link) == "{} link".format(attachment_link.attachment)


def test_file_type_group_by():
    file_type_1 = AttachmentFileTypeFactory(
        label='ft1',
        group=["group1", "group2"],
    )
    file_type_2 = AttachmentFileTypeFactory(
        label='ft2',
        group=["group1"],
    )
    file_type_3 = AttachmentFileTypeFactory(
        label='ft3',
        group=["group3"],
    )
    assert list(models.FileType.objects.group_by("group1")) == [
        file_type_1,
        file_type_2,
    ]
    assert list(models.FileType.objects.group_by(["group1", "group2"])) == [
        file_type_1,
    ]
    assert list(models.FileType.objects.group_by("group3")) == [file_type_3]
