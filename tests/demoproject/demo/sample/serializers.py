from rest_framework import serializers

from unicef_attachments.fields import AttachmentSingleFileField, FileTypeModelChoiceField
from unicef_attachments.models import FileType
from unicef_attachments.serializers import AttachmentSerializerMixin

from demo.sample.models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class AuthorBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"


class AuthorFileTypeSerializer(AuthorBaseSerializer):
    file_type = FileTypeModelChoiceField(
        queryset=FileType.objects.filter(code='author_profile_image')
    )


class AuthorSerializer(AttachmentSerializerMixin, AuthorBaseSerializer):
    profile_image = AttachmentSingleFileField()


class AuthorOverrideSerializer(AttachmentSerializerMixin, AuthorBaseSerializer):
    profile_image = AttachmentSingleFileField(override="image")
