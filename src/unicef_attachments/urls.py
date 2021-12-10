from django.urls import re_path

from unicef_attachments import views

app_name = 'attachments'

urlpatterns = (
    re_path(
        r'^$',
        view=views.AttachmentListView.as_view(),
        name='list'
    ),
    re_path(
        r'^file/(?P<pk>\d+)/$',
        view=views.AttachmentFileView.as_view(),
        name='file'
    ),
    re_path(
        r'^links/(?P<app>[\w\.]+)/(?P<model>\w+)/(?P<object_pk>\d+)/$',
        view=views.AttachmentLinkListCreateView.as_view(),
        name='link'
    ),
    re_path(
        r'^links/(?P<pk>\d+)/$',
        view=views.AttachmentLinkDeleteView.as_view(),
        name='link-delete'
    ),
    re_path(
        r'^upload/$',
        view=views.AttachmentCreateView.as_view(),
        name='create'
    ),
)
