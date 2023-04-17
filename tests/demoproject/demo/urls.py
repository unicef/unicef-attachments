from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(r"^sample/", include("demo.sample.urls")),
    path(r"^attachments/", include("unicef_attachments.urls")),
    path(r"^admin/", admin.site.urls),
]
