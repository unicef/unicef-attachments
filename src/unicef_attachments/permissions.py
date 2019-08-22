from rest_framework.permissions import IsAuthenticated


class AttachmentPermissions(IsAuthenticated):
    """Default attachment permissions"""
