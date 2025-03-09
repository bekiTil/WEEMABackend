from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import User
from WEEMA.models import BaseModel
import uuid

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('super_admin', 'SUPER_ADMIN'),
        ('facilitator', 'FACILITATOR'),
        ('cluster_manager', 'CLUSTER_MANAGER'),
        ('shg_lead', 'SHG_LEAD'),
    ]
    user_type = models.CharField(max_length=40, choices=USER_TYPES)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups', 
        blank=True,
        help_text='The groups this user belongs to.',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  
        blank=True,
        help_text='Specific permissions for this user.',
    )
    
    can_download_report = models.BooleanField(default=False)
    
    def __str__(self):
        return "username" + str(self.username) if self.username else "Unknown"

class WEEMAEntities(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.URLField(null=True)
    last_login = models.DateTimeField(auto_now=True)
    verification_note = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    
    def delete(self, *args, **kwargs):
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)