from unicef_attachments.utils import get_attachment_flat_model, get_object_link


def filepath_prefix():
    return "sample"


def denormalize(attachment):
    flat, created = get_attachment_flat_model().objects.update_or_create(
        attachment=attachment, defaults={"object_link": get_object_link(attachment)}
    )

    return flat
