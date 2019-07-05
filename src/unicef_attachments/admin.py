from django.contrib import admin
from django.contrib.contenttypes import admin as ct_admin
from ordered_model.admin import OrderedModelAdmin

from unicef_attachments import models as app_models


@admin.register(app_models.FileType)
class FileTypeAdmin(OrderedModelAdmin):
    list_display = ['label', 'name', 'code', 'group', 'move_up_down_links']
    list_filter = ['code', ]
    search_fields = ['name', 'label']


@admin.register(app_models.Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = [
        'file_type',
        'file',
        'modified',
        'uploaded_by',
    ]
    list_filter = ['file_type', 'uploaded_by', ]


class AttachmentInlineAdminMixin:
    def save_formset(self, request, form, formset, change):
        instances = formset.save()
        for instance in instances:
            instance.code = formset.code
            instance.save()


class AttachmentInline(ct_admin.GenericTabularInline):
    model = app_models.Attachment
    extra = 0
    fields = ('file', 'hyperlink', 'modified', 'uploaded_by', )
    readonly_fields = ('modified', 'uploaded_by', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(code=self.code)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.code = self.code
        return formset


class AttachmentSingleInline(AttachmentInline):
    def has_add_permission(self, request):
        return False
