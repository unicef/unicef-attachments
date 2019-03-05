import magic
from django import forms
from django.conf import settings
from django.utils.translation import gettext as _


class SafeFileValidator:
    def __init__(self, **kwargs):
        self.mime_lookup_length = kwargs.pop("mime_lookup_length", 4096)
        self.invalid_content_types = getattr(
            settings,
            "ATTACHMENT_INVALID_FILE_TYPES",
            [
                "application/x-msdownload",
                "applications/x-ms-installer",
                "application/x-sh",
                "text/x-perl",
                "text/x-python",
            ],
        )

    def __call__(self, value):
        errors = []
        data_file = value.file
        uploaded_content_type = getattr(data_file, 'content_type', '')

        mg = magic.Magic(mime=True)
        content_type_magic = mg.from_buffer(
            data_file.read(self.mime_lookup_length)
        )
        data_file.seek(0)

        # Prefer mime-type from magic over mime-type from http header
        if uploaded_content_type != content_type_magic:
            uploaded_content_type = content_type_magic

        if uploaded_content_type in self.invalid_content_types:
            errors.append(
                _(f'Unsupported file type: {content_type_magic}.')
            )
        if errors:
            raise forms.ValidationError(errors)
