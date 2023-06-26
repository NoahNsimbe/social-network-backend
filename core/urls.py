from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import SimpleRouter

from core.api.auth.views import AuthViewSet
from core.api.posts.views import PostViewSet
from core.api.user.views import UserViewSet

router = SimpleRouter(trailing_slash=False)

router.register(r"users", UserViewSet, basename="user")
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    path(r"api/", include(router.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
