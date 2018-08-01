from django.core.management.base import BaseCommand

from unicef_attachments.models import Attachment
from unicef_attachments.utils import denormalize_attachment, get_attachment_flat_model


class Command(BaseCommand):
    """Denormalize all attachments"""

    def handle(self, *args, **options):
        attachment_qs = Attachment.objects.exclude(
            pk__in=get_attachment_flat_model().objects.values_list(
                "attachment_id",
                flat=True
            )
        )
        for attachment in attachment_qs:
            denormalize_attachment(attachment)
