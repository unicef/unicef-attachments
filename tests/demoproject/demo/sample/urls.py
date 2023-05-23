from rest_framework import routers

from demo.sample import views

app_name = "sample"

router = routers.DefaultRouter()
router.register(r"authors/", views.AuthorViewSet)
router.register(r"books/", views.BookViewSet)

urlpatterns = router.urls
