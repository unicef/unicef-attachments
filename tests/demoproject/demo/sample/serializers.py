from demo.sample.models import Author, Book
from rest_framework import serializers

from unicef_attachments.fields import FileTypeModelChoiceField
from unicef_attachments.models import FileType


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class AuthorSerializer(serializers.ModelSerializer):
    file_type = FileTypeModelChoiceField(
        queryset=FileType.objects.filter(code='author_profile_image')
    )
    books = BookSerializer(many=True, required=False)

    class Meta:
        model = Author
        fields = "__all__"
