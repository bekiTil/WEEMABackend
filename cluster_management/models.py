from django.db import models
from user_management.models import WEEMAEntities
from WEEMA.models import BaseModel
from django.core.exceptions import ValidationError

# Cluster Model
class Cluster(BaseModel):
    cluster_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    total_groups = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255, null=True, blank=True)
    cluster_manager = models.ForeignKey(WEEMAEntities, on_delete=models.SET_NULL, null=True, related_name="coordinated_clusters")
    description = models.TextField(blank=True, null=True)

    def increment_total_groups(self):
        self.total_groups += 1
        self.save()

    def decrement_total_groups(self):
        if self.total_groups > 0:
            self.total_groups -= 1
            self.save()

    def __str__(self):
        return self.cluster_name



# Self Help Group Model
class SelfHelpGroup(BaseModel):
    group_name = models.CharField(max_length=255)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name="groups", null=True, blank=True)
    facilitator = models.ForeignKey(
        WEEMAEntities,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facilitated_groups"
    )
    group_leader = models.ForeignKey(WEEMAEntities, on_delete=models.SET_NULL, null=True, related_name="led_groups")
    total_members = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    location = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    Zone = models.CharField(max_length=255, null=True, blank=True)
    woreda = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def clean(self):
        # A group must be associated with either a cluster or a facilitator,
        # but not both at the same time.
        if not self.cluster and not self.facilitator:
            raise ValidationError("A group must be associated with either a cluster or a facilitator.")
        if self.cluster and self.facilitator:
            raise ValidationError("A group cannot be associated with both a cluster and a facilitator at the same time.")

    
    def increment_totals(self):
        self.total_members += 1
        self.save()

    def decrement_totals(self):
        if self.total_members > 0:
            self.total_members -= 1
        self.save()

    def save(self, *args, **kwargs):
        self.clean()
        # is_new = self._state.adding
        # if not is_new:
        #     old_cluster = SelfHelpGroup.objects.get(pk=self.pk).cluster
        #     if old_cluster != self.cluster:
        #         old_cluster.decrement_total_groups()
        #         self.cluster.increment_total_groups()
        # else:
        #     self.cluster.increment_total_groups()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        cluster = self.cluster
        super().delete(*args, **kwargs)
        # cluster.decrement_total_groups()

    def __str__(self):
        return self.group_name



# Member Model
class Member(BaseModel):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]

    RELIGION_CHOICES = [
        ('christianity', 'Christianity'),
        ('islam', 'Islam'),
        ('traditional', 'Traditional'),
        ('other', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    hh_size = models.PositiveIntegerField(null=True, blank=True)  # Household size
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES, null=True, blank=True)
    is_other_shg_member_in_house = models.BooleanField(default=False)
    how_many_shg_members = models.PositiveIntegerField(null=True, blank=True)
    is_responsible_for_children = models.BooleanField(default=False)
    contact_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    group = models.ForeignKey('SelfHelpGroup', on_delete=models.CASCADE, related_name="members")
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        # if not is_new:
        #     old_group = Member.objects.get(pk=self.pk).group
        #     if old_group != self.group:
        #         old_group.decrement_totals()
        #         self.group.increment_totals()
        # else:
        #     self.group.increment_totals()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        group = self.group
        super().delete(*args, **kwargs)
        # group.decrement_totals()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


