from urllib.parse import urljoin

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from unicef_attachments.models import Attachment, AttachmentLink
from unicef_attachments.serializers import (
    AttachmentFileUploadSerializer,
    AttachmentFlatSerializer,
    AttachmentLinkSerializer,
)
from unicef_attachments.utils import get_attachment_flat_model


class AttachmentListView(ListAPIView):
    queryset = get_attachment_flat_model().objects.exclude(
        Q(attachment__file__isnull=True) | Q(attachment__file__exact=""),
        Q(attachment__hyperlink__isnull=True) | Q(attachment__hyperlink__exact="")
    )
    permission_classes = (IsAdminUser, )
    serializer_class = AttachmentFlatSerializer


class AttachmentLinkListCreateView(ListCreateAPIView):
    permission_classes = (IsAdminUser, )
    serializer_class = AttachmentLinkSerializer

    def set_content_object(self):
        try:
            self.content_type = ContentType.objects.get_by_natural_key(
                self.kwargs.get("app"),
                self.kwargs.get("model"),
            )
        except ContentType.DoesNotExist:
            raise NotFound()

        try:
            self.object_id = self.kwargs.get("object_pk")
            model_cls = self.content_type.model_class()
            self.content_object = model_cls.objects.get(
                pk=self.object_id
            )
        except model_cls.DoesNotExist:
            raise NotFound()

    def get_queryset(self):
        self.set_content_object()
        return AttachmentLink.objects.filter(
            content_type=self.content_type,
            object_id=self.object_id,
        )

    def perform_create(self, serializer):
        self.set_content_object()
        serializer.save()
        instance = serializer.instance
        instance.content_type = self.content_type
        instance.object_id = self.object_id
        instance.save()


class AttachmentLinkDeleteView(DestroyAPIView):
    queryset = AttachmentLink.objects.all()
    permission_classes = (IsAdminUser, )
    serializer_class = AttachmentLinkSerializer


class AttachmentFileView(DetailView):
    model = Attachment

    def get(self, *args, **kwargs):
        try:
            attachment = Attachment.objects.get(pk=kwargs["pk"])
        except Attachment.DoesNotExist:
            return HttpResponseNotFound(
                _("No Attachment matches the given query.")
            )
        if not attachment or (not attachment.file and not attachment.hyperlink):
            return HttpResponseNotFound(
                _("Attachment has no file or hyperlink")
            )
        url = urljoin(
            "https://{}".format(self.request.get_host()),
            attachment.url
        )
        return HttpResponseRedirect(url)


class AttachmentCreateView(CreateAPIView):
    queryset = Attachment.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = AttachmentFileUploadSerializer
    parser_classes = (FileUploadParser,)

    def perform_create(self, serializer):
        self.instance = serializer.save()

    def post(self, *args, **kwargs):
        super(AttachmentCreateView, self).post(*args, **kwargs)
        return Response(
            AttachmentFlatSerializer(
                get_attachment_flat_model().objects.filter(
                    attachment=self.instance
                ).first()
            ).data
        )


class AttachmentUpdateView(UpdateAPIView):
    queryset = Attachment.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = AttachmentFileUploadSerializer
    parser_classes = (FileUploadParser,)

    def perform_update(self, serializer):
        # force the updating of the uploaded by field to current user
        # this is not set when PATCH request made
        serializer.instance.uploaded_by = serializer.context["request"].user
        self.instance = serializer.save()

    def put(self, *args, **kwargs):
        super(AttachmentUpdateView, self).put(*args, **kwargs)
        return Response(
            AttachmentFlatSerializer(
                get_attachment_flat_model().objects.filter(
                    attachment=self.instance
                ).first()
            ).data
        )

    def patch(self, *args, **kwargs):
        super(AttachmentUpdateView, self).patch(*args, **kwargs)
        return Response(
            AttachmentFlatSerializer(
                get_attachment_flat_model().objects.filter(
                    attachment=self.instance
                ).first()
            ).data
        )
