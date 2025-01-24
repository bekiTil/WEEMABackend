from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SixMonthDataViewSet, AnnualDataViewSet, AnnualChildrenStatusViewSet

router = DefaultRouter()
router.register(r"six-month-data", SixMonthDataViewSet)
router.register(r"annual-data", AnnualDataViewSet)
router.register(r"annual-children-status", AnnualChildrenStatusViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
