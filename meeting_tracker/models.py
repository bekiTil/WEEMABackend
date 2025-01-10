from django.db import models
from cluster_management.models import SelfHelpGroup, Member
from WEEMA.models import BaseModel

class Meeting(BaseModel):
    group = models.ForeignKey(SelfHelpGroup, on_delete=models.CASCADE, related_name="meetings")
    agenda = models.TextField()
    notes = models.TextField()
    meeting_date = models.DateTimeField()

    def __str__(self):
        return f"Meeting for {self.group.group_name} on {self.meeting_date}"


class Attendance(BaseModel):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="attendances")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="attendances")
    attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member} - {'Attended' if self.attended else 'Absent'}"
