from collections import defaultdict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str


def _filepath_prefix():
    return None


def get_filepath_prefix_func():
    try:
        dotted_path = settings.ATTACHMENT_FILEPATH_PREFIX_FUNC
        assert dotted_path is not None
        module, func_name = dotted_path.rsplit('.', 1)
        module, func = smart_str(module), smart_str(func_name)
        func = getattr(__import__(module, {}, {}, [func]), func)
        return func
    except ImportError as e:
        raise ImproperlyConfigured(
            'Could not import ATTACHMENT_FILEPATH_PREFIX_FUNC {}: {}'.format(
                settings.ATTACHMENT_FILEPATH_PREFIX_FUNC,
                e
            )
        )
    except (AssertionError, AttributeError):
        return _filepath_prefix


filepath_prefix = get_filepath_prefix_func()()


def _attachment_flat_model():
    from unicef_attachments.models import AttachmentFlat
    return AttachmentFlat


def get_attachment_flat_model():
    try:
        dotted_path = settings.ATTACHMENT_FLAT_MODEL
        assert dotted_path is not None
        module, func_name = dotted_path.rsplit('.', 1)
        module, func = smart_str(module), smart_str(func_name)
        func = getattr(__import__(module, {}, {}, [func]), func)
        return func
    except ImportError as e:
        raise ImproperlyConfigured(
            'Could not import ATTACHMENT_FLAT_MODEL {}: {}'.format(
                settings.ATTACHMENT_FLAT_MODEL,
                e
            )
        )
    except (AssertionError, AttributeError):
        return _attachment_flat_model()


def _attachment_permissions():
    from unicef_attachments.permissions import AttachmentPermissions
    return AttachmentPermissions


def get_attachment_permissions():
    try:
        dotted_path = settings.ATTACHMENT_PERMISSIONS
        assert dotted_path is not None
        module, func_name = dotted_path.rsplit('.', 1)
        module, func = smart_str(module), smart_str(func_name)
        func = getattr(__import__(module, {}, {}, [func]), func)
        return func
    except ImportError as e:
        raise ImproperlyConfigured(
            'Could not import ATTACHMENT_PERMISSIONS {}: {}'.format(
                settings.ATTACHMENT_PERMISSIONS,
                e
            )
        )
    except (AssertionError, AttributeError):
        return _attachment_permissions()


def get_file_type(obj):
    if obj.file_type:
        return obj.file_type.label
    else:
        return ""


def get_object_link(obj):
    try:
        return obj.content_object.get_object_url()
    except AttributeError:
        return ""


def denormalize_attachment(attachment):
    uploaded_by = attachment.uploaded_by.get_full_name() if attachment.uploaded_by else ""
    flat, created = get_attachment_flat_model().objects.update_or_create(
        attachment=attachment,
        defaults={
            "object_link": get_object_link(attachment),
            "file_type": get_file_type(attachment),
            "file_link": attachment.file_link,
            "filename": attachment.filename,
            "uploaded_by": uploaded_by,
            "created": attachment.created.strftime("%d %b %Y"),
        }
    )
    return flat


def get_denormalize_func():
    try:
        dotted_path = settings.ATTACHMENT_DENORMALIZE_FUNC
        assert dotted_path is not None
        module, func_name = dotted_path.rsplit('.', 1)
        module, func = smart_str(module), smart_str(func_name)
        func = getattr(__import__(module, {}, {}, [func]), func)
        return func
    except ImportError as e:
        raise ImproperlyConfigured(
            'Could not import ATTACHMENT_DENORMALIZE_FUNC {}: {}'.format(
                settings.ATTACHMENT_DENORMALIZE_FUNC,
                e
            )
        )
    except (AssertionError, AttributeError):
        return denormalize_attachment


def get_matching_key(file_type, keys):
    key = (file_type.label.lower(), file_type.name.lower())
    for k in keys:
        if k[0] == key[0] or k[1] == key[1]:
            return k
    return key


def cleanup_filetypes():
    """Combine FileTypes that have the same label/name

    Get a list of the duplicates, include pk and group values
    Update the group record for primary record
    Update all attachment file type fields with primary record
    Remove duplicate file type records
    """
    from unicef_attachments.models import Attachment, FileType

    # get duplicates
    duplicates = defaultdict(list)
    for file_type in FileType.objects.order_by("pk"):
        key = get_matching_key(file_type, duplicates.keys())
        duplicates[key].append((file_type.pk, file_type.group))

    for key, dups in duplicates.items():
        if len(dups) > 1:
            primary_pk, _ = dups.pop(0)
            primary_file_type = FileType.objects.get(pk=primary_pk)
            for pk, group in dups:
                if not primary_file_type.group:
                    primary_file_type.group = []
                primary_file_type.group += group
                primary_file_type.save()
                Attachment.objects.filter(file_type__pk=pk).update(
                    file_type=primary_file_type,
                )
                FileType.objects.get(pk=pk).delete()
