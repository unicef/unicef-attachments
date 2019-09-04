from rest_framework.permissions import IsAdminUser


class AttachmentPermOverride(IsAdminUser):
    """Demo permission override"""
