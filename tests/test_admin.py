import pytest

from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_attachment_inline_get(client, author, superuser):
    client.force_login(superuser)
    response = client.get(
        reverse("admin:sample_author_change", args=[author.pk]),
    )
    assert response.status_code == 200


def test_attachment_inline_post(client, author, superuser, upload_file):
    client.force_login(superuser)
    assert not author.profile_image.exists()
    form_key = "unicef_attachments-attachment-content_type-object_id"
    response = client.post(
        reverse("admin:sample_author_change", args=[author.pk]),
        data={
            f"{form_key}-TOTAL_FORMS": "1",
            f"{form_key}-INITIAL_FORMS": "0",
            f"{form_key}-MAX_NUM_FORMS": "",
            "first_name": author.first_name,
            "last_name": author.last_name,
            f"{form_key}-0-file": upload_file,
        },
        follow=True
    )
    assert response.status_code == 200
    assert author.profile_image.exists()
