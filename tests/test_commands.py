import pytest
from django.core.management import call_command
from tests.factories import AttachmentFactory, AttachmentFileTypeFactory, UserFactory

from unicef_attachments.utils import get_attachment_flat_model

pytestmark = pytest.mark.django_db


def test_denormalize_attachment():
    user = UserFactory()
    code = "test_code"
    file_type = AttachmentFileTypeFactory(code=code)
    attachment = AttachmentFactory(
        file_type=file_type,
        code=code,
        file="sample1.pdf",
        content_object=file_type,
        uploaded_by=user
    )
    AttachmentFlat = get_attachment_flat_model()
    flat_qs = AttachmentFlat.objects.filter(attachment=attachment)
    assert flat_qs.exists()
    AttachmentFlat.objects.get(attachment=attachment).delete()
    assert not flat_qs.exists()

    call_command("denormalize_attachments")

    assert flat_qs.exists()
