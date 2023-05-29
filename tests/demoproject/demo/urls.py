from django.contrib import admin
from django.urls import include, re_path

urlpatterns = [
    re_path(r"^sample/", include("demo.sample.urls")),
    re_path(r"^attachments/", include("unicef_attachments.urls")),
    re_path(r"^admin/", admin.site.urls),
]
