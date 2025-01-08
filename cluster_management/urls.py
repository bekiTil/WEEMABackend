from rest_framework.routers import DefaultRouter
from .views import ClusterViewSet, SelfHelpGroupViewSet, MemberViewSet, SixMonthSavingViewSet

router = DefaultRouter()
router.register(r'clusters', ClusterViewSet)
router.register(r'self-help-groups', SelfHelpGroupViewSet)
router.register(r'members', MemberViewSet)
router.register(r'six-month-savings', SixMonthSavingViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]