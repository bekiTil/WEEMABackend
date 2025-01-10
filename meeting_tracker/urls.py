from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingViewSet, AttendanceViewSet, MeetingAttendanceAPIView

router = DefaultRouter()
router.register(r'meetings', MeetingViewSet)
router.register(r'attendances', AttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('attendees/<uuid:meeting_id>/', MeetingAttendanceAPIView.as_view(), name='meeting-attendance')
]
