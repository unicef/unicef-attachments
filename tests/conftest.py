import base64
import tempfile

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

import pytest

from tests import factories


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return factories.UserFactory(is_staff=True)


@pytest.fixture
def superuser():
    return factories.UserFactory(
        username="superusername",
        email="super@example.com",
        is_superuser=True,
        is_staff=True,
    )


@pytest.fixture
def file_type():
    return factories.AttachmentFileTypeFactory()


@pytest.fixture
def base64_file():
    file_content = 'these are the file contents!'.encode('utf-8')
    return 'data:text/plain;base64,{}'.format(base64.b64encode(file_content))


@pytest.fixture
def upload_file():
    return SimpleUploadedFile(
        'hello_world.txt',
        u'hello world!'.encode('utf-8')
    )


@pytest.fixture()
def headers(upload_file):
    return {
        "HTTP_CONTENT_TYPE": "multipart/form-data",
        "HTTP_CONTENT_DISPOSITION": "attachment; filename={}".format(
            upload_file.name
        )
    }


@pytest.fixture
def data_file():
    return tempfile.NamedTemporaryFile(suffix=".pdf")


@pytest.fixture
def author():
    return factories.AuthorFactory()


@pytest.fixture
def book():
    return factories.BookFactory()


@pytest.fixture
def attachment(file_type, author):
    return factories.AttachmentFactory(
        file_type=file_type,
        code=file_type.code,
        content_object=author,
        file="test.pdf",
    )


@pytest.fixture
def attachment_blank(file_type, author):
    return factories.AttachmentFactory(
        file_type=file_type,
        code=file_type.code,
        content_object=author,
    )


@pytest.fixture
def attachment_empty():
    return factories.AttachmentFactory(
        file="blank.pdf"
    )


@pytest.fixture
def attachment_uri(file_type, author):
    return factories.AttachmentFactory(
        file_type=file_type,
        code=file_type.code,
        content_object=author,
        hyperlink="https://example.com/sample.pdf",
    )


@pytest.fixture
def attachment_link(attachment, book):
    content_type = ContentType.objects.get_for_model(book)
    return factories.AttachmentLinkFactory(
        attachment=attachment,
        content_type=content_type,
        object_id=book.pk,
    )
