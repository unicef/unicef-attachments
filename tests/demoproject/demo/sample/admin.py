from demo.sample.models import Author
from django.contrib import admin

from unicef_attachments.admin import AttachmentInlineAdminMixin, AttachmentSingleInline


class ProfileImageInline(AttachmentSingleInline):
    code = 'author_profile_image'


@admin.register(Author)
class AuthorAdmin(AttachmentInlineAdminMixin, admin.ModelAdmin):
    model = Author
    inlines = [ProfileImageInline]
