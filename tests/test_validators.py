import pytest
from django.forms import ValidationError

from unicef_attachments.validators import SafeFileValidator


def test_safe_file_valid(upload_file):
    validator = SafeFileValidator()
    assert validator((upload_file, "filename")) is None


def test_safe_file_invalid(upload_file, settings):
    settings.ATTACHMENT_INVALID_FILE_TYPES = ["text/plain"]
    validator = SafeFileValidator()
    with pytest.raises(ValidationError):
        validator((upload_file, "filename"))
