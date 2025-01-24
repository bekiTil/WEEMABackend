# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClusterViewSet, SelfHelpGroupViewSet, MemberViewSet

router = DefaultRouter()
router.register(r'clusters', ClusterViewSet)
router.register(r'self-help-groups', SelfHelpGroupViewSet)
router.register(r'members', MemberViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]