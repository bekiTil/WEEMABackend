# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomUserViewSet,
    WEEMAEntitiesViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'weema-entities', WEEMAEntitiesViewSet, basename='weema-entities')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
