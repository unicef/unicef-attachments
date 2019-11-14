from unittest.mock import Mock, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from tests.factories import AttachmentFactory, AttachmentFileTypeFactory
from unicef_attachments.models import Attachment, AttachmentLink

pytestmark = pytest.mark.django_db


def test_attachment_list_get_forbidden(client):
    response = client.get(reverse("attachments:list"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_attachment_list_get_no_file(client, attachment_blank, user):
    assert not attachment_blank.file
    client.force_login(user)
    response = client.get(reverse("attachments:list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


def test_attachment_list_get_file(client, attachment, user):
    client.force_login(user)
    response = client.get(reverse("attachments:list"))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == attachment.pk
    assert data[0]["file_type_id"] == attachment.file_type.pk


def test_attachment_list_get_hyperlink(client, attachment_uri, user):
    client.force_login(user)
    assert attachment_uri.hyperlink
    response = client.get(reverse("attachments:list"))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == attachment_uri.pk


def test_attachment_list_filter(client, attachment, user):
    client.force_login(user)
    response = client.get("{}?filename={}".format(
        reverse("attachments:list"),
        attachment.filename
    ))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == attachment.pk


def test_attachment_list_filter_not_found(client, attachment, user):
    client.force_login(user)
    response = client.get("{}?filename=wrong".format(
        reverse("attachments:list"),
    ))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0


def test_attachment_file_not_found(client, user):
    client.force_login(user)
    response = client.get(reverse("attachments:file", args=[404]))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert b"No Attachment matches the given query" in response.content


def test_attachment_file_no_url(client, attachment_blank, user):
    client.force_login(user)
    response = client.get(
        reverse("attachments:file", args=[attachment_blank.pk])
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert b"Attachment has no file or hyperlink" in response.content


def test_attachment_file_redirect(client, attachment, user):
    client.force_login(user)
    response = client.get(reverse("attachments:file", args=[attachment.pk]))
    assert response.status_code == status.HTTP_302_FOUND


def test_attachment_create_forbidden(client, upload_file, headers):
    response = client.get(
        reverse("attachments:create"),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_attachment_create_get(client, upload_file, user, headers):
    client.force_login(user)
    response = client.get(
        reverse("attachments:create"),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_attachment_create_put(client, upload_file, user, headers):
    client.force_login(user)
    response = client.put(
        reverse("attachments:create"),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_attachment_create_patch(client, upload_file, user, headers):
    client.force_login(user)
    response = client.patch(
        reverse("attachments:create"),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_attachment_create_post_invalid_type(
        client,
        upload_file,
        user,
        headers,
):
    client.force_login(user)
    attachment_qs = Attachment.objects
    assert not attachment_qs.exists()
    mock_magic = Mock()
    mock_magic.from_buffer.return_value = "text/x-python"
    with patch(
            "unicef_attachments.validators.magic.Magic",
            Mock(return_value=mock_magic),
    ):
        response = client.post(
            reverse("attachments:create"),
            data={"file": upload_file},
            **headers
        )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"file": [
        "Unsupported file type: text/x-python."
    ]}


def test_attachment_create_post(client, upload_file, user, headers):
    client.force_login(user)
    attachment_qs = Attachment.objects
    assert not attachment_qs.exists()
    response = client.post(
        reverse("attachments:create"),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["file_link"]
    assert attachment_qs.exists()
    attachment = attachment_qs.first()
    assert attachment.content_object is None
    assert attachment.file_type is None


@pytest.mark.skip("removed endpoint")
def test_attachment_update_forbidden(client, attachment, upload_file, headers):
    response = client.get(
        reverse("attachments:update", args=[attachment.pk]),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.skip("removed endpoint")
def test_attachment_update_get(client, attachment, upload_file, user, headers):
    client.force_login(user)
    response = client.get(
        reverse("attachments:update", args=[attachment.pk]),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.skip("removed endpoint")
def test_attachment_update_post(client, attachment, upload_file, user, headers):
    client.force_login(user)
    response = client.get(
        reverse("attachments:update", args=[attachment.pk]),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.skip("removed endpoint")
def test_attachment_update_put(api_client, attachment_blank, upload_file, user, headers):
    api_client.force_login(user)
    assert not attachment_blank.file
    response = api_client.put(
        reverse("attachments:update", args=[attachment_blank.pk]),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == attachment_blank.pk
    assert data["file_link"] == reverse(
        "attachments:file",
        args=[attachment_blank.pk]
    )
    attachment_update = Attachment.objects.get(pk=attachment_blank.pk)
    assert attachment_update.file


@pytest.mark.skip("removed endpoint")
def test_attachment_update_patch(api_client, attachment_blank, upload_file, user, headers):
    api_client.force_login(user)
    assert not attachment_blank.file
    response = api_client.patch(
        reverse("attachments:update", args=[attachment_blank.pk]),
        data={"file": upload_file},
        **headers
    )
    assert response.status_code == status.HTTP_200_OK
    attachment_update = Attachment.objects.get(pk=attachment_blank.pk)
    assert attachment_update.file
    data = response.json()
    assert data["file_link"] == reverse(
        "attachments:file",
        args=[attachment_blank.pk]
    )


@pytest.mark.skip("removed endpoint")
def test_attachment_update_put_target(api_client, attachment_blank, upload_file, user, headers):
    api_client.force_login(user)
    """Ensure update only affects specified attachment"""
    attachment = AttachmentFactory()
    assert not attachment_blank.file
    assert not attachment.file
    response = api_client.put(
        reverse("attachments:update", args=[attachment_blank.pk]),
        data={"file": upload_file},
        format="multipart"
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == attachment_blank.pk
    assert data["file_link"] == reverse(
        "attachments:file",
        args=[attachment_blank.pk]
    )
    attachment_update = Attachment.objects.get(pk=attachment_blank.pk)
    assert attachment_update.file
    other_attachment_update = Attachment.objects.get(pk=attachment.pk)
    assert not other_attachment_update.file


def test_attachment_single_file_field(client, author, user):
    file_type = AttachmentFileTypeFactory(code="author_profile_image")
    attachment = AttachmentFactory(
        content_object=author,
        file_type=file_type,
        code=file_type.code,
        file="test.pdf",
    )
    client.force_login(user)
    response = client.get(reverse("sample:author-detail", args=[author.pk]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["profile_image"].endswith(attachment.file.name)


def test_attachment_single_file_field_no_value(client, author, user):
    file_type = AttachmentFileTypeFactory(code="author_profile_image")
    AttachmentFactory(
        content_object=author,
        file_type=file_type,
        code=file_type.code,
    )
    client.force_login(user)
    response = client.get(reverse("sample:author-detail", args=[author.pk]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["profile_image"] is None


def test_attachment_link_empty(client, book, user):
    client.force_login(user)
    content_type = ContentType.objects.get_for_model(book)
    response = client.get(reverse("attachments:link", args=[
        content_type.app_label,
        content_type.model,
        book.pk
    ]))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_attachment_link_empty_no_found_content_type(client, book, user):
    client.force_login(user)
    response = client.get(reverse("attachments:link", args=[
        "sample",
        "wrong",
        book.pk
    ]))
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_attachment_link_list(client, book, attachment_link, user):
    client.force_login(user)
    content_type = ContentType.objects.get_for_model(book)
    assert attachment_link.content_object == book
    response = client.get(reverse("attachments:link", args=[
        content_type.app_label,
        content_type.model,
        book.pk
    ]))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == attachment_link.pk
    assert data[0]["filename"] == attachment_link.attachment.filename


def test_attachment_link_add(client, attachment, book, user):
    client.force_login(user)
    content_type = ContentType.objects.get_for_model(book)
    attachment_link_qs = AttachmentLink.objects.filter(
        content_type=content_type,
        object_id=book.pk,
    )
    assert not attachment_link_qs.exists()
    response = client.post(
        reverse("attachments:link", args=[
            content_type.app_label,
            content_type.model,
            book.pk
        ]),
        data={"attachment": attachment.pk}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert attachment_link_qs.exists()
    data = response.json()
    assert data["attachment"] == attachment.pk
    assert data["filename"] == attachment.filename
    attachment_link = attachment_link_qs.first()
    assert attachment_link.content_object == book


def test_attachment_link_delete(client, attachment_link, user):
    client.force_login(user)
    attachment_link_qs = AttachmentLink.objects.filter(pk=attachment_link.pk)
    assert attachment_link_qs.exists()
    response = client.delete(
        reverse("attachments:link-delete", args=[attachment_link.pk]),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not attachment_link_qs.exists()
