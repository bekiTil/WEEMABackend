from django.db.models import Sum, Avg, Count, Max, Min, F, Q, DecimalField
from cluster_management.models import SelfHelpGroup, Member
from data_collection.models import AnnualData, SixMonthData, AnnualChildrenStatus, AnnualSelfHelpGroupData
import csv
from datetime import datetime

 

def get_location_level_group_report(start_date = None, end_date = None, cluster = None):
    # Parse optional date range parameters
    date_filter = Q()
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            date_filter = Q(created_at__range=[start_date, end_date])
        except Exception as e:
            return {"error": str(e)}

    # Get distinct, non-empty location values from SelfHelpGroup
    locations = (SelfHelpGroup.objects
                    .exclude(region__isnull=True)
                    .exclude(region__exact="")
                    .values_list('region', flat=True)
                    .distinct())

    report_data = [["Location", "Total Groups", "Total Members", "Total hh size", "Total Savings", "Total Capital", "Total Loan Circulated","Avg Iga Capital"]]

    # For each unique location, aggregate analytics across groups and members
    for loc in locations:
        # Groups at this location
        if cluster:
            groups = SelfHelpGroup.objects.filter(region=loc, cluster = cluster)
        else:
            groups = SelfHelpGroup.objects.filter(region=loc)
        total_groups = groups.count()

        # Members in these groups
        members = Member.objects.filter(group__in=groups)
        total_members = members.count()

        # Total household size from members (using Member.hh_size)
        total_household_size = members.aggregate(total=Sum('hh_size'))['total'] or 0

        # Aggregate financial metrics using related data (filtered by date range if provided)
        total_savings = (AnnualData.objects.filter(member__in=members).filter(date_filter)
                            .aggregate(total=Sum('total_savings', output_field=DecimalField()))['total'] or 0)

        total_capital = (SixMonthData.objects.filter(member__in=members).filter(date_filter)
                            .aggregate(total=Sum('iga_capital', output_field=DecimalField()))['total'] or 0)

        total_loan_circulated = (SixMonthData.objects.filter(member__in=members).filter(date_filter)
                                    .aggregate(total=Sum('loan_amount_received_shg', output_field=DecimalField()))['total'] or 0)

        average_iga_capital = (SixMonthData.objects.filter(member__in=members).filter(date_filter)
                                .aggregate(avg=Avg('iga_capital', output_field=DecimalField()))['avg'] or 0)

        report_data.append([
            loc,
            total_groups,
            total_members,
            total_household_size,
            total_savings,
            total_capital,
            total_loan_circulated,
            average_iga_capital,
        ])

    return report_data


def get_location_level_loan_saving_report(start_date = None, end_date = None, cluster = None):
    
    date_filter = Q()
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            date_filter = Q(created_at__range=[start_date, end_date])
        except Exception as e:
            return {"error": str(e)}
        
    # Get distinct, non-empty location values from SelfHelpGroup
    locations = (
        SelfHelpGroup.objects
        .exclude(region__isnull=True)
        .exclude(region__exact="")
        .values_list('region', flat=True)
        .distinct()
    )
    
    # Prepare CSV header
    csv_data = [
        [
            "Entity", 
            "Total Members", 
            "Max Loan Round", 
            "IGA Capital Range",  
            "Total Other Loans", 
            "Loan by Purpose", 
            "Savings Range", 
        ]
    ]
    
    # Iterate over each location and aggregate data
    for loc in locations:
        
        if cluster:
            groups = SelfHelpGroup.objects.filter(region=loc, cluster = cluster)
        else:
            groups = SelfHelpGroup.objects.filter(region=loc)
            
        members = Member.objects.filter(group__in=groups)
        total_members = members.count()
        
        # Aggregations from SixMonthData for these members
        max_loan_round = SixMonthData.objects.filter(member__in=members).filter(date_filter).aggregate(
            max_loan=Max('loan_amount_received_shg', output_field=DecimalField())
        )['max_loan']
        
        iga_capital_range = SixMonthData.objects.filter(member__in=members).filter(date_filter).aggregate(
            min_iga=Min('iga_capital', output_field=DecimalField()),
            max_iga=Max('iga_capital', output_field=DecimalField())
        )
        
        total_loan_other_sources = SixMonthData.objects.filter(member__in=members).filter(date_filter).aggregate(
            total_loan_other_sources=Sum('loan_amount_from_other_sources', output_field=DecimalField())
        )['total_loan_other_sources']
        
        loan_by_purpose_qs = SixMonthData.objects.filter(member__in=members).filter(date_filter).values('purpose_of_loan').annotate(
            total_loan=Sum('loan_amount_received_shg', output_field=DecimalField())
        )
        loan_by_purpose = ', '.join([f"{item['purpose_of_loan']}: {item['total_loan']}" for item in loan_by_purpose_qs])
        
        # Aggregations from AnnualData for these members
        savings_range = AnnualData.objects.filter(member__in=members).filter(date_filter).aggregate(
            min_savings=Min('total_savings', output_field=DecimalField()),
            max_savings=Max('total_savings', output_field=DecimalField())
        )
        
        iga_min =iga_capital_range.get('min_iga') if  iga_capital_range.get('min_iga') else 0
        iga_max = iga_capital_range.get('max_iga') if  iga_capital_range.get('max_iga') else 0
        saving_min = savings_range.get('min_savings') if  savings_range.get('min_savings') else 0
        saving_max = savings_range.get('max_savings') if savings_range.get('max_savings') else 0
        
        # Append row of aggregated data for the current location
        row = [
            loc,
            total_members,
            max_loan_round,
            str(iga_min) + " - "+ str(iga_max),
            total_loan_other_sources,
            loan_by_purpose,
            str(saving_min) + " - " + str(saving_max),
            
        ]
        csv_data.append(row)
    
    
    return csv_data





def get_location_level_hh_report(start_date = None, end_date = None, cluster = None):
    
    date_filter = Q()
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            date_filter = Q(created_at__range=[start_date, end_date])
        except Exception as e:
            return {"error": str(e)}
        
        
    # Get all locations
    locations = (
        SelfHelpGroup.objects
        .exclude(region__isnull=True)
        .exclude(region__exact="")
        .values_list('region', flat=True)
        .distinct()
    )
    
    # Prepare CSV data
    csv_data = [
        [
            "Regions",
            "Total Members",
            "Total Household Size",
            "Average Meals Per Day",
            "Total Child Morbidity",
            "Total Child Mortality",
            "% School Enrollment",
        ]
    ]

    # Process each location
    for loc in locations:
        # Get groups in this location
        if cluster:
            groups = SelfHelpGroup.objects.filter(region=loc, cluster = cluster)
        else:
            groups = SelfHelpGroup.objects.filter(region=loc)
        
        # Get all members in those groups
        members = Member.objects.filter(group__in=groups)

        if not members.exists():
            continue  # Skip locations with no members

        # Aggregate data
        total_members = members.count()

        total_household_size = (
            AnnualData.objects.filter(member__in=members).filter(date_filter).aggregate(total=Sum("household_size", output_field=DecimalField()))["total"] or 0
        )

        avg_meals_per_day = (
            SixMonthData.objects.filter(member__in=members).filter(date_filter)
            .aggregate(
                avg_meals=Avg(F("meals_per_day_for_children") + F("meals_per_day_for_adults"), output_field=DecimalField())
            )["avg_meals"]
        )

        total_child_morbidity = (
            SixMonthData.objects.filter(member__in=members).filter(date_filter)
            .aggregate(
                morbidity=Sum(F("days_diarrhea_children") + F("days_other_illness_children"), output_field=DecimalField())
            )["morbidity"]
        )

        total_child_mortality = (
            AnnualData.objects.filter(member__in=members).filter(date_filter).aggregate(total=Sum("mortality_children_under_5", output_field=DecimalField()))["total"]
        )

        # School Enrollment Calculation
        school_age_children = 0
        enrolled_children = 0
        children_statuses = AnnualChildrenStatus.objects.filter(member__in=members)
        for status in children_statuses:
            for i in range(1, 6):  # Assuming up to 5 children per member
                school_status = getattr(status, f"child_{i}_school_status", None)
                if school_status:
                    school_age_children += 1
                    if school_status == "enrolled":
                        enrolled_children += 1

        percentage_school_enrollment = (
            (enrolled_children / school_age_children) * 100 if school_age_children > 0 else None
        )

        # Append data to CSV
        csv_data.append([
            loc,
            total_members,
            total_household_size,
            avg_meals_per_day,
            total_child_morbidity,
            total_child_mortality,
            percentage_school_enrollment,
        ])

    return csv_data


def dump_all_data_report(start_date = None, end_date = None, cluster = None, facilitator = None):
    
    date_filter = Q()
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            date_filter = Q(created_at__range=[start_date, end_date])
        except Exception as e:
            return {"error": str(e)}
        
    groups = SelfHelpGroup.objects.filter(cluster=cluster)
    
    if cluster:
        groups = SelfHelpGroup.objects.filter(cluster=cluster)
    elif facilitator:
        groups = SelfHelpGroup.objects.filter(facilitator=facilitator)
    else:
        groups = SelfHelpGroup.objects.all()
    
    members = Member.objects.filter(group__in=groups)
   
    
    
    annual_member_data = AnnualData.objects.filter(member__in=members).filter(date_filter)
    member_sixmonth_data = SixMonthData.objects.filter(member__in=members).filter(date_filter)
    annual_childeren_status = AnnualChildrenStatus.objects.filter(member__in=members).filter(date_filter)
    annual_group_status =AnnualSelfHelpGroupData.objects.filter(group__in=groups)
    
    print("Members count:", members.count())
    print("Number of groups:", groups.count())
    print("Number of annual member data entries:", annual_member_data.count())
    print("Number of six month data entries:", member_sixmonth_data.count())
    print("Number of annual children status entries:", annual_childeren_status.count())
    print("Number of annual group status entries:", annual_group_status.count())
    
    # Prepare lists for each section
    annual_data_list = [
        ["cluster", "group","member", "age", "gender", "education_level", "marital_status", "family_size", "household_size", 
         "total_savings", "loan_rounds_taken", "estimated_value_of_household_assets", "household_decision_making",
         "community_decision_making", "mortality_children_under_5", "mortality_other_household_members", 
         "housing", "have_latrine", "electricity", "drinking_water"]
    ]

    for data in annual_member_data:
        annual_data_list.append([data.member.group.cluster.cluster_name, data.member.group.group_name, data.member.first_name + " " + data.member.last_name, data.member.age, data.member.gender, data.education_level, 
                                 data.marital_status, data.family_size, data.household_size, 
                                 data.total_savings, data.loan_rounds_taken, 
                                 data.estimated_value_of_household_assets, data.household_decision_making, 
                                 data.community_decision_making, data.mortality_children_under_5, 
                                 data.mortality_other_household_members, data.housing, 
                                 data.have_latrine, data.electricity, data.drinking_water])

    six_month_data_list = [
        ["cluster", "group", "member", "active_iga", "iga_activity_code", "iga_capital", "loan_amount_received_shg", 
         "loan_source_code", "loan_amount_from_other_sources", "purpose_of_loan", "approx_monthly_personal_income",
         "approx_monthly_household_income", "meals_per_day_for_children", "meals_per_day_for_adults", 
         "days_diarrhea_children", "days_other_illness_children", "days_diarrhea_others", "days_other_illness_others"]
    ]

    for data in member_sixmonth_data:
        six_month_data_list.append([data.member.group.cluster.cluster_name, data.member.group.group_name, data.member.first_name + " " + data.member.last_name, data.active_iga, data.iga_activity_code, data.iga_capital, 
                                    data.loan_amount_received_shg, data.loan_source_code, 
                                    data.loan_amount_from_other_sources, data.purpose_of_loan, 
                                    data.approx_monthly_personal_income, data.approx_monthly_household_income, 
                                    data.meals_per_day_for_children, data.meals_per_day_for_adults, 
                                    data.days_diarrhea_children, data.days_other_illness_children, 
                                    data.days_diarrhea_others, data.days_other_illness_others])

    children_status_list = [
        ["cluster", "group", "member", "number_of_children", "child_1_name", "child_1_gender", "child_1_age", "child_1_school_status",
         "child_2_name", "child_2_gender", "child_2_age", "child_2_school_status", "child_3_name", 
         "child_3_gender", "child_3_age", "child_3_school_status", "child_4_name", "child_4_gender", 
         "child_4_age", "child_4_school_status", "child_5_name", "child_5_gender", "child_5_age", "child_5_school_status"]
    ]

    for status in annual_childeren_status:
        children_status_list.append([status.member.group.cluster.cluster_name, status.member.group.group_name, status.member.first_name + " " + status.member.last_name, status.number_of_children, status.child_1_name, 
                                     status.child_1_gender, status.child_1_age, status.child_1_school_status,
                                     status.child_2_name, status.child_2_gender, status.child_2_age, 
                                     status.child_2_school_status, status.child_3_name, status.child_3_gender, 
                                     status.child_3_age, status.child_3_school_status, status.child_4_name, 
                                     status.child_4_gender, status.child_4_age, status.child_4_school_status, 
                                     status.child_5_name, status.child_5_gender, status.child_5_age, 
                                     status.child_5_school_status])

    group_status_list = [
        ["cluster","group", "amount_regular_saving", "shg_capital", "num_members_taken_loan", "smallest_loan_given", 
         "largest_loan_given", "amount_loans_written_off", "amount_invested_in_group_iga", "group_iga_code1", 
         "description", "income_social_savings", "expenditure_social_savings", "num_shg_members_social_support", 
         "num_people_outside_shg_social_support", "num_other_supporting_institutions", "min_monthly_personal", 
         "training_received_per_year", "shg_member_health_care_support_amount", "other_member_health_care_support_amount", 
         "other_insurance_need_amount", "other_social_need_amount", "others", "training_received_in_year"]
    ]

    for status in annual_group_status:
        group_status_list.append([status.group.cluster.cluster_name, status.group.group_name, status.amount_regular_saving, status.shg_capital, 
                                  status.num_members_taken_loan, status.smallest_loan_given, 
                                  status.largest_loan_given, status.amount_loans_written_off, 
                                  status.amount_invested_in_group_iga, status.group_iga_code1, 
                                  status.description, status.income_social_savings, status.expenditure_social_savings, 
                                  status.num_shg_members_social_support, status.num_people_outside_shg_social_support, 
                                  status.num_other_supporting_institutions, status.min_monthly_personal, 
                                  status.training_received_per_year, status.shg_member_health_care_support_amount, 
                                  status.other_member_health_care_support_amount, status.other_insurance_need_amount, 
                                  status.other_social_need_amount, status.others, status.training_received_in_year])

    # Return the data as a dictionary with corresponding lists
    return {
        "annual_data": annual_data_list,
        "six_month_data": six_month_data_list,
        "children_status": children_status_list,
        "group_status": group_status_list
    } 