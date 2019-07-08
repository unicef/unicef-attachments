import pytest
from demo.sample.models import AttachmentFlatOverride
from demo.sample.utils import denormalize, filepath_prefix
from django.core.exceptions import ImproperlyConfigured

from tests.factories import AttachmentFactory, AttachmentFileTypeFactory
from unicef_attachments import utils
from unicef_attachments.models import AttachmentFlat, FileType

pytestmark = pytest.mark.django_db


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


def test_get_denormalize_func_default():
    assert utils.get_denormalize_func() == utils.denormalize_attachment


def test_get_denormalize_func_override(settings):
    settings.ATTACHMENT_DENORMALIZE_FUNC = "demo.sample.utils.denormalize"
    assert utils.get_denormalize_func() == denormalize


def test_get_denormalize_func_invalid(settings):
    settings.ATTACHMENT_DENORMALIZE_FUNC = "demo.sample.wrong.denormalize"
    with pytest.raises(ImproperlyConfigured):
        utils.get_denormalize_func()


def test_get_matching_key(file_type):
    key = (file_type.label.lower(), file_type.name.lower())

    # name matches
    name_key = ("something", file_type.name.lower())
    assert name_key == utils.get_matching_key(file_type, [name_key])

    # label matches
    label_key = (file_type.label.lower(), "something")
    assert label_key == utils.get_matching_key(file_type, [label_key])

    # no matches
    assert key == utils.get_matching_key(file_type, [("some", "thing")])


def test_cleanup_file_types():
    file_type_1 = AttachmentFileTypeFactory(
        label="Other",
        name="something",
    )
    file_type_2 = AttachmentFileTypeFactory(
        label="Other",
        name="different",
    )
    file_type_3 = AttachmentFileTypeFactory(
        label="PD",
        name="pd",
    )
    file_type_4 = AttachmentFileTypeFactory(
        label="FT4",
        name="something",
    )
    attachment_1 = AttachmentFactory(file_type=file_type_1)
    attachment_2 = AttachmentFactory(file_type=file_type_2)
    attachment_3 = AttachmentFactory(file_type=file_type_3)
    attachment_4 = AttachmentFactory(file_type=file_type_4)

    utils.cleanup_filetypes()

    attachment_1.refresh_from_db()
    assert attachment_1.file_type == file_type_1
    attachment_2.refresh_from_db()
    assert attachment_2.file_type == file_type_1
    attachment_3.refresh_from_db()
    assert attachment_3.file_type == file_type_3
    attachment_4.refresh_from_db()
    assert attachment_4.file_type == file_type_1

    assert not FileType.objects.filter(pk=file_type_2.pk).exists()
    assert not FileType.objects.filter(pk=file_type_4.pk).exists()
