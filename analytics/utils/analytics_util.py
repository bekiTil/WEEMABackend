from django.db.models import Sum, Avg, Count, Max, Min, F, Q, DecimalField
from cluster_management.models import SelfHelpGroup, Member
from data_collection.models import AnnualData, SixMonthData, AnnualChildrenStatus
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
                    .exclude(location__isnull=True)
                    .exclude(location__exact="")
                    .values_list('location', flat=True)
                    .distinct())

    report_data = [["Location", "Total Groups", "Total Members", "Total hh size", "Total Savings", "Total Capital", "Total Loan Circulated","Avg Iga Capital"]]

    # For each unique location, aggregate analytics across groups and members
    for loc in locations:
        # Groups at this location
        if cluster:
            groups = SelfHelpGroup.objects.filter(location=loc, cluster = cluster)
        else:
            groups = SelfHelpGroup.objects.filter(location=loc)
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
        .exclude(location__isnull=True)
        .exclude(location__exact="")
        .values_list('location', flat=True)
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
            groups = SelfHelpGroup.objects.filter(location=loc, cluster = cluster)
        else:
            groups = SelfHelpGroup.objects.filter(location=loc)
            
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
        .exclude(location__isnull=True)
        .exclude(location__exact="")
        .values_list('location', flat=True)
        .distinct()
    )
    
    # Prepare CSV data
    csv_data = [
        [
            "Location",
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
            groups = SelfHelpGroup.objects.filter(location=loc, cluster = cluster)
        else:
            groups = SelfHelpGroup.objects.filter(location=loc)
        
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
