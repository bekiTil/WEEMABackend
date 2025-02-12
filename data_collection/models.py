from django.db import models
from cluster_management.models import Member, SelfHelpGroup
from WEEMA.models import BaseModel

class SixMonthData(BaseModel):
    # Choices for IGA Activities
    IGA_CHOICES = [
        ("agriculture", "Agriculture"),
        ("petty_trading", "Petty Trading"),
        ("manufacturing", "Manufacturing"),
        ("service", "Service"),
        ("others", "Others"),
    ]

    # Choices for Loan Received from Other Sources
    LOAN_SOURCE_CHOICES = [
        ("cla", "CLA"),
        ("micro_finance", "Micro-finance"),
        ("bank", "Bank"),
        ("local_money_lenders", "Local Money Lenders"),
        ("others", "Others"),
    ]

    # Choices for Purpose of Loan
    PURPOSE_CHOICES = [
        ("iga", "IGA"),
        ("social_events", "Social Events"),
        ("furniture", "Furniture"),
        ("education", "Education"),
        ("others", "Others"),
    ]

    # Model Fields
    member  = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="six_month_members")
    active_iga = models.BooleanField(default=False, verbose_name="Active IGA?")
    iga_activity_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="IGA Activity Code", choices=IGA_CHOICES)
    iga_capital = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loan_amount_received_shg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Loan Amount Received in Period (SHG)")
    loan_source_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Source (Code)", choices=LOAN_SOURCE_CHOICES)
    loan_amount_from_other_sources = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Amount from other Source")
    
    purpose_of_loan = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    approx_monthly_personal_income = models.DecimalField(max_digits=10, decimal_places=2)
    approx_monthly_household_income = models.DecimalField(max_digits=10, decimal_places=2)
    meals_per_day_for_children = models.IntegerField()
    meals_per_day_for_adults = models.IntegerField()
    days_diarrhea_children = models.IntegerField()
    days_other_illness_children = models.IntegerField()
    days_diarrhea_others = models.IntegerField()
    days_other_illness_others = models.IntegerField()

class AnnualData(BaseModel):
    # Choices for Marital Status
    MARITAL_STATUS_CHOICES = [
        ("single", "Single"),
        ("married", "Married"),
        ("divorced", "Divorced"),
        ("widowed", "Widowed"),
    ]

    # Choices for Household and Community Decision Making
    DECISION_MAKING_CHOICES = [
        ("informed", "Informed"),
        ("consulted", "Consulted"),
        ("consent", "Consent"),
    ]

    # Choices for Housing Type
    HOUSING_CHOICES = [
        ("metal_sheet", "Metal Sheet"),
        ("wood", "Wood"),
        ("mud", "Mud"),
        ("bricks", "Bricks"),
        ("concrete", "Concrete"),
        ("others", "Others"),
    ]

    # Choices for Drinking Water
    DRINKING_WATER_CHOICES = [
        ("piped_inside", "Piped Water Inside the House"),
        ("piped_outside", "Piped Water Outside the House"),
        ("water_point", "Water Point"),
        ("protected_well", "Protected Well"),
        ("unprotected_well", "Unprotected Well"),
        ("river_stream", "River/Stream"),
        ("other", "Other (Specify)"),
    ]
    
    # Choices for IGA Activities
    IGA_ACTIVITY_CHOICES = [
        ("agriculture", "Agriculture"),
        ("petty_trading", "Petty Trading"),
        ("manufacturing", "Manufacturing"),
        ("service", "Service"),
        ("others", "Others"),
    ]

    # Choices for Training Received
    TRAINING_RECEIVED_CHOICES = [
        ("shg_concept", "SHG Concept"),
        ("saving_and_credit", "Saving and Credit"),
        ("record_keeping", "Record Keeping"),
        ("facilitation_skill", "Facilitation Skill"),
        ("leadership", "Leadership"),
        ("self_assessment", "Self-Assessment"),
        ("cla_fla_concept", "CLA & FLA Concept"),
    ]
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    # Model Fields
    member  = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="annual_data_members")
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    education_level = models.CharField(max_length=100)
    marital_status = models.CharField(max_length=50, choices=MARITAL_STATUS_CHOICES)
    family_size = models.IntegerField()
    household_size = models.IntegerField()
    total_savings = models.DecimalField(max_digits=10, decimal_places=2)
    loan_rounds_taken = models.IntegerField()
    estimated_value_of_household_assets = models.DecimalField(max_digits=15, decimal_places=2)
    household_decision_making = models.CharField(max_length=50, choices=DECISION_MAKING_CHOICES, verbose_name="Household Decision Making")
    community_decision_making = models.CharField(max_length=50, choices=DECISION_MAKING_CHOICES, verbose_name="Community Decision Making")
    mortality_children_under_5 = models.IntegerField()
    mortality_other_household_members = models.IntegerField()
    housing = models.CharField(max_length=50, choices=HOUSING_CHOICES)
    have_latrine = models.BooleanField(default=False, verbose_name="Have Latrine?")
    electricity = models.BooleanField(default=False, verbose_name="Electricity?")
    drinking_water = models.CharField(max_length=50, choices=DRINKING_WATER_CHOICES, verbose_name="Drinking Water Source")

    def __str__(self):
        return f"Annual Data for Household with {self.members} Members"



class AnnualChildrenStatus(BaseModel):
    # Choices for Gender
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    # Choices for School Status
    SCHOOL_STATUS_CHOICES = [
        ("enrolled", "Enrolled"),
        ("not_enrolled", "Not Enrolled"),
        ("dropped_out", "Dropped Out"),
        ("graduated", "Graduated"),
    ]

    # Number of Children
    member  = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="children_of_members")
    number_of_children = models.IntegerField(default=0, verbose_name="Number of Children")

    # Child 1
    child_1_name = models.CharField(max_length=100, null=True, blank=True)
    child_1_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    child_1_age = models.IntegerField(null=True, blank=True)
    child_1_school_status = models.CharField(max_length=20, choices=SCHOOL_STATUS_CHOICES, null=True, blank=True)

    # Child 2
    child_2_name = models.CharField(max_length=100, null=True, blank=True)
    child_2_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    child_2_age = models.IntegerField(null=True, blank=True)
    child_2_school_status = models.CharField(max_length=20, choices=SCHOOL_STATUS_CHOICES, null=True, blank=True)

    # Child 3
    child_3_name = models.CharField(max_length=100, null=True, blank=True)
    child_3_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    child_3_age = models.IntegerField(null=True, blank=True)
    child_3_school_status = models.CharField(max_length=20, choices=SCHOOL_STATUS_CHOICES, null=True, blank=True)

    # Child 4
    child_4_name = models.CharField(max_length=100, null=True, blank=True)
    child_4_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    child_4_age = models.IntegerField(null=True, blank=True)
    child_4_school_status = models.CharField(max_length=20, choices=SCHOOL_STATUS_CHOICES, null=True, blank=True)

    # Child 5
    child_5_name = models.CharField(max_length=100, null=True, blank=True)
    child_5_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    child_5_age = models.IntegerField(null=True, blank=True)
    child_5_school_status = models.CharField(max_length=20, choices=SCHOOL_STATUS_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"Household with {self.number_of_children} children"



class AnnualSelfHelpGroupData(BaseModel):
    group = models.ForeignKey(SelfHelpGroup, on_delete=models.CASCADE, related_name="annualGroupData")
    amount_regular_saving = models.DecimalField(max_digits=10, decimal_places=2)
    shg_capital = models.DecimalField(max_digits=10, decimal_places=2)
    num_members_taken_loan = models.PositiveIntegerField()
    smallest_loan_given = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    largest_loan_given = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_loans_written_off = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_invested_in_group_iga = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    group_iga_code1 = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    income_social_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expenditure_social_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    num_shg_members_social_support = models.PositiveIntegerField(default=0)
    num_people_outside_shg_social_support = models.PositiveIntegerField(default=0)
    num_other_supporting_institutions = models.PositiveIntegerField(default=0)
    min_monthly_personal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    training_received_per_year = models.PositiveIntegerField(default=0) 
    shg_member_health_care_support_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    other_member_health_care_support_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    other_insurance_need_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    other_social_need_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    others = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
