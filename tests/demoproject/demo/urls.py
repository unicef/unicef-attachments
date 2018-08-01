from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^sample/', include('demo.sample.urls')),
    url(r'^attachments/', include('unicef_attachments.urls')),
    url(r'^admin/', admin.site.urls),
]
