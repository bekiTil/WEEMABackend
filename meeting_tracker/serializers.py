from rest_framework import serializers
from .models import Meeting, Attendance

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'group', 'agenda', 'notes', 'meeting_date']

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'meeting', 'member', 'attended']
