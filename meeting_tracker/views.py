from rest_framework import viewsets
from rest_framework.response import Response
from .models import Meeting, Attendance
from .serializers import MeetingSerializer, AttendanceSerializer
from cluster_management.serializers import MemberSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['group', 'agenda', 'meeting_date']
    search_fields = ['agenda', 'notes', ]
    ordering_fields = ['meeting_date', 'created_at', 'updated_at']

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['meeting', 'member', 'attended']
    search_fields = ['meeting', 'member', 'attended']
    ordering_fields = ['created_at', 'updated_at']



class MeetingAttendanceAPIView(APIView):
    """
    API view to get the attendance status of a meeting.
    """
    
    def get_attendance_status(meeting_id):
        """
        Helper function to get the attendance status for a given meeting.
        Returns a dictionary with 'attended' and 'missed' lists.
        """
        meeting = Meeting.objects.get(id=meeting_id)
        attendances = Attendance.objects.filter(meeting=meeting)

        attended_members = []
        missed_members = []

        for attendance in attendances:
            if attendance.attended:
                attended_members.append(attendance.member)
            else:
                missed_members.append(attendance.member)

        return {
            'attended': attended_members,
            'missed': missed_members
        }


    def get(self, request, meeting_id):
        try:
            # Get the attendance status for the meeting
            attendance_status = get_attendance_status(meeting_id)

            # Serialize the member data (assuming you have a MemberSerializer)
            attended_members_data = MemberSerializer(attendance_status['attended'], many=True).data
            missed_members_data = MemberSerializer(attendance_status['missed'], many=True).data

            # Return the response with the lists of attended and missed members
            return Response({
                'attended_members': attended_members_data,
                'missed_members': missed_members_data,
            }, status=status.HTTP_200_OK)

        except Meeting.DoesNotExist:
            return Response({"detail": "Meeting not found."}, status=status.HTTP_404_NOT_FOUND)
