import pytest
from demo.sample.models import AttachmentFlatOverride
from demo.sample.permissions import AttachmentPermOverride
from demo.sample.utils import denormalize, filepath_prefix
from django.core.exceptions import ImproperlyConfigured

from unicef_attachments import utils
from unicef_attachments.models import AttachmentFlat
from unicef_attachments.permissions import AttachmentPermissions


def test_get_filepath_prefix_func_default():
    assert utils.get_filepath_prefix_func() == utils._filepath_prefix


def test_get_filepath_prefix_func_override(settings):
    settings.ATTACHMENT_FILEPATH_PREFIX_FUNC = "demo.sample.utils.filepath_prefix"
    assert utils.get_filepath_prefix_func() == filepath_prefix


def test_get_filepath_prefix_func_invalid(settings):
    settings.ATTACHMENT_FILEPATH_PREFIX_FUNC = "demo.wrong.filepath_prefix"
    with pytest.raises(ImproperlyConfigured):
        utils.get_filepath_prefix_func()


def test_get_attachment_flat_model_default():
    assert utils.get_attachment_flat_model() == AttachmentFlat


def test_get_attachment_flat_model_override(settings):
    settings.ATTACHMENT_FLAT_MODEL = "demo.sample.models.AttachmentFlatOverride"
    assert utils.get_attachment_flat_model() == AttachmentFlatOverride


def test_get_attachment_flat_model_invalid(settings):
    settings.ATTACHMENT_FLAT_MODEL = "demo.sample.wrong.AttachmentFlatOverride"
    with pytest.raises(ImproperlyConfigured):
        utils.get_attachment_flat_model()


def test_get_attachment_permissions_default():
    assert utils.get_attachment_permissions() == AttachmentPermissions


def test_get_attachment_permissions_override(settings):
    settings.ATTACHMENT_PERMISSIONS = "demo.sample.permissions.AttachmentPermOverride"
    assert utils.get_attachment_permissions() == AttachmentPermOverride


def test_get_attachment_permissions_invalid(settings):
    settings.ATTACHMENT_PERMISSIONS = "demo.sample.wrong.AttachmentPermOverride"
    with pytest.raises(ImproperlyConfigured):
        utils.get_attachment_permissions()


def test_get_denormalize_func_default():
    assert utils.get_denormalize_func() == utils.denormalize_attachment


def test_get_denormalize_func_override(settings):
    settings.ATTACHMENT_DENORMALIZE_FUNC = "demo.sample.utils.denormalize"
    assert utils.get_denormalize_func() == denormalize


def test_get_denormalize_func_invalid(settings):
    settings.ATTACHMENT_DENORMALIZE_FUNC = "demo.sample.wrong.denormalize"
    with pytest.raises(ImproperlyConfigured):
        utils.get_denormalize_func()
