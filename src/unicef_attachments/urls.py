from django.conf.urls import url

from unicef_attachments import views

app_name = 'attachments'

urlpatterns = (
    url(
        r'^$',
        view=views.AttachmentListView.as_view(),
        name='list'
    ),
    url(
        r'^file/(?P<pk>\d+)/$',
        view=views.AttachmentFileView.as_view(),
        name='file'
    ),
    url(
        r'^links/(?P<app>[\w\.]+)/(?P<model>\w+)/(?P<object_pk>\d+)/$',
        view=views.AttachmentLinkListCreateView.as_view(),
        name='link'
    ),
    url(
        r'^links/(?P<pk>\d+)/$',
        view=views.AttachmentLinkDeleteView.as_view(),
        name='link-delete'
    ),
    url(
        r'^upload/$',
        view=views.AttachmentCreateView.as_view(),
        name='create'
    ),
    url(
        r'^upload/(?P<pk>\d+)/$',
        view=views.AttachmentUpdateView.as_view(),
        name='update'
    ),
)
