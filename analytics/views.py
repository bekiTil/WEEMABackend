from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Avg, Max, Min, F, Q
from data_collection.models import SixMonthData, AnnualData, AnnualChildrenStatus
from user_management.models import WEEMAEntities
from cluster_management.models import SelfHelpGroup, Cluster, Member
from user_management.models import CustomUser
from django.utils.dateparse import parse_datetime
from django.contrib.auth.models import AnonymousUser
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import csv
from django.http import HttpResponse
# ReportLab imports
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet

from io import BytesIO
from datetime import datetime

from .utils.analytics_util import get_location_level_group_report, get_location_level_loan_saving_report, get_location_level_hh_report  


class SystemLevelReportView(APIView):
    """
    System-level report aggregating data across all clusters, groups, and members with optional date range filtering.
    """

    def get(self, request):
        # Parsing date range parameters
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)

        # Filtering data based on the time range
        filters = {}
        if start_date and end_date:
            filters['created_at__range'] = [start_date, end_date]

        # Aggregating data
        total_shgs = SelfHelpGroup.objects.count()
        total_members = Member.objects.count()
        total_household_size = Member.objects.aggregate(total=Sum('hh_size'))['total']
        total_savings = AnnualData.objects.filter(**filters).aggregate(total=Sum('total_savings'))['total']
        total_capital = SixMonthData.objects.filter(**filters).aggregate(total=Sum('iga_capital'))['total']
        total_loan_circulated = SixMonthData.objects.filter(**filters).aggregate(total=Sum('loan_amount_received_shg'))['total']
        average_iga_capital = SixMonthData.objects.filter(**filters).aggregate(avg=Avg('iga_capital'))['avg']

        return Response({
            'total_shgs': total_shgs,
            'total_members': total_members,
            'total_household_size': total_household_size,
            'total_savings': total_savings,
            'total_capital': total_capital,
            'total_loan_circulated': total_loan_circulated,
            'average_iga_capital': average_iga_capital,
        }, status=status.HTTP_200_OK)

class ClusterLevelReportView(APIView):
    """
    Cluster-level report, aggregated for a given cluster.
    """
    def get(self, request, cluster_id):
        # Parsing date range parameters
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)

        # Get the cluster
        try:
            cluster = Cluster.objects.get(id=cluster_id)
        except Cluster.DoesNotExist:
            return Response({"error": "Cluster not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get all groups and members in the cluster
        groups = SelfHelpGroup.objects.filter(cluster=cluster)
        members = Member.objects.filter(group__in=groups)

        # Filtering data based on the time range
        filters = {}
        if start_date and end_date:
            filters['created_at__range'] = [start_date, end_date]

        # Aggregating data
        total_shgs = groups.count()
        total_members = members.count()
        total_household_size = members.aggregate(total=Sum('hh_size'))['total']
        total_savings = AnnualData.objects.filter(member__in=members, **filters).aggregate(total=Sum('total_savings'))['total']
        total_capital = SixMonthData.objects.filter(member__in=members, **filters).aggregate(total=Sum('iga_capital'))['total']
        total_loan_circulated = SixMonthData.objects.filter(member__in=members, **filters).aggregate(total=Sum('loan_amount_received_shg'))['total']
        average_iga_capital = SixMonthData.objects.filter(member__in=members, **filters).aggregate(avg=Avg('iga_capital'))['avg']

        return Response({
            'cluster': cluster.cluster_name,
            'total_shgs': total_shgs,
            'total_members': total_members,
            'total_household_size': total_household_size,
            'total_savings': total_savings,
            'total_capital': total_capital,
            'total_loan_circulated': total_loan_circulated,
            'average_iga_capital': average_iga_capital,
        }, status=status.HTTP_200_OK)


class SelfHelpGroupLevelReportView(APIView):
    """
    Self-help group-level report, aggregated for a given self-help group.
    """
    def get(self, request, group_id):
        # Parsing date range parameters
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)

        # Get the self-help group
        try:
            group = SelfHelpGroup.objects.get(id=group_id)
        except SelfHelpGroup.DoesNotExist:
            return Response({"error": "SelfHelpGroup not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get all members in the group
        members = Member.objects.filter(group=group)

        # Filtering data based on the time range
        filters = {}
        if start_date and end_date:
            filters['created_at__range'] = [start_date, end_date]

        # Aggregating data
        total_members = members.count()
        total_household_size = members.aggregate(total=Sum('hh_size'))['total']
        total_savings = AnnualData.objects.filter(member__in=members, **filters).aggregate(total=Sum('total_savings'))['total']
        total_capital = SixMonthData.objects.filter(member__in=members, **filters).aggregate(total=Sum('iga_capital'))['total']
        total_loan_circulated = SixMonthData.objects.filter(member__in=members, **filters).aggregate(total=Sum('loan_amount_received_shg'))['total']
        average_iga_capital = SixMonthData.objects.filter(member__in=members, **filters).aggregate(avg=Avg('iga_capital'))['avg']
        
        # Prepare data response
        json_report_data = {
            "group_name": group.group_name,
            "total_members": total_members,
            "total_household_size": total_household_size,
            "total_savings": total_savings,
            "total_capital": total_capital,
            "total_loan_circulated": total_loan_circulated,
            "average_iga_capital": average_iga_capital,
        }
        
        response_format = request.query_params.get('format', 'json')

        if response_format == 'csv':
            csv_data = [
                ['Group Name', 'Total Members', 'Total Household Size', 'Total Savings', 'Total Capital', 'Total Loan Circulated', 'Average IGA Capital'],
                [group.group_name, total_members, total_household_size, total_savings, total_capital, total_loan_circulated, average_iga_capital],
            ]

            # Create the CSV response
            csv_response = HttpResponse(content_type='text/csv')
            csv_response['Content-Disposition'] = f'attachment; filename="{group.group_name}_report.csv"'
            
            writer = csv.writer(csv_response)
            writer.writerows(csv_data)

            return csv_response
        
        return Response(json_report_data, status=status.HTTP_200_OK)
            
        
class DashboardMetricsView(APIView):
    """
    Dashboard metrics based on user role (Super Admin, Cluster Admin, Group Admin).
    """

    
    def get(self, request):
        # Determine user type
        user = request.user
        
        user_type = 'super_admin'
        if not isinstance(request.user, AnonymousUser):
            user_type = user.user_type
        

        # Extract cluster_id or group_id from request query parameters
        cluster_id = request.query_params.get('cluster_id', None)
        group_id = request.query_params.get('group_id', None)

        # Parse date range (optional for growth metrics)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)

        # Super Admin: System-wide data
        if user_type == 'super_admin':
            data = {
                "total_clusters": Cluster.objects.count(),
                "total_groups": SelfHelpGroup.objects.count(),
                "total_members": Member.objects.count(),
                "total_savings": AnnualData.objects.aggregate(total_savings=Sum('total_savings'))['total_savings'],
                "member_growth": self.get_member_growth_graph(
                                                            start_date=start_date, 
                                                            end_date=end_date, 
                                                            cluster_id=cluster_id, 
                                                            group_id=group_id
                                                        ),
                "entities": self.get_entity_growth_graph(start_date=start_date, end_date=end_date,cluster_id=cluster_id )
            }
            return Response(data, status=status.HTTP_200_OK)

        # Cluster Admin: Data for the specified cluster
        elif user_type == 'cluster_manager':
            if not cluster_id:
                return Response({"error": "Cluster ID is required for cluster managers."}, status=status.HTTP_400_BAD_REQUEST)

            data = {
                "total_groups": SelfHelpGroup.objects.filter(cluster=cluster_id).count(),
                "total_members": Member.objects.filter(group__cluster=cluster_id).count(),
                "total_savings": AnnualData.objects.filter(member__group__cluster=cluster_id).aggregate(
                    total_savings=Sum('total_savings')
                )['total_savings'],
                "member_growth": self.get_member_growth_graph(
                                                            start_date=start_date, 
                                                            end_date=end_date, 
                                                            cluster_id=cluster_id, 
                                                            group_id=group_id
                                                        ),
            }
            return Response(data, status=status.HTTP_200_OK)

        # Group Admin: Data for the specified group
        elif user_type == 'shg_lead':
            if not group_id:
                return Response({"error": "Group ID is required for group admins."}, status=status.HTTP_400_BAD_REQUEST)

            data = {
                "total_members": Member.objects.filter(group_id=group_id).count(),
                "total_savings": AnnualData.objects.filter(member__group_id=group_id).aggregate(
                    total_savings=Sum('total_savings')
                )['total_savings'],
                "member_growth": self.get_member_growth_graph(
                                                            start_date=start_date, 
                                                            end_date=end_date, 
                                                            cluster_id=cluster_id, 
                                                            group_id=group_id
                                                        ),
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_entity_growth_graph(self, start_date, end_date, cluster_id=None):
        """
        Generate data for entity growth graph over time (e.g., monthly), divided by user type.
        """
        filters = {}
        if start_date and end_date:
            filters['created_at__range'] = [start_date, end_date]
        # if cluster_id:
        #     filters['cluster'] = cluster_id  # Assuming users are linked to clusters

        # Group by month and user type, then count new users
        growth_data = (
            CustomUser.objects.filter(user_type__in=['facilitator', 'cluster_manager', 'shg_lead'], **filters)
            .annotate(month=TruncMonth('created_at'))
            .values('month', 'user_type')
            .annotate(total_users=Count('id'))
            .order_by('month', 'user_type')
        )

        # Convert to a list of dictionaries for graph consumption
        return [
            {
                "month": entry['month'].strftime('%Y-%m'),
                "user_type": entry['user_type'],
                "total_users": entry['total_users']
            }
            for entry in growth_data
        ]

    def get_member_growth(self, start_date, end_date, cluster_id=None, group_id=None):
        """
        Calculate member growth over time, optionally filtered by cluster or group.
        """
        filters = {}
        if start_date and end_date:
            filters['created_at__range'] = [start_date, end_date]
        if cluster_id:
            filters['group__cluster'] = cluster_id
        if group_id:
            filters['group_id'] = group_id

        growth_data = Member.objects.filter(**filters).values('gender').annotate(
            count=Count('id')
        )
        return list(growth_data)

    def get_entity_counts(self, cluster_id=None):
        """
        Count entities (facilitators, cluster managers, SHG leads), optionally filtered by cluster.
        """
        # Fetch all relevant users
        users = CustomUser.objects.filter(user_type__in=['facilitator', 'cluster_manager', 'shg_lead'])

        # Calculate counts
        return {
            "facilitators": users.filter(user_type='facilitator').count(),
            "cluster_managers": users.filter(user_type='cluster_manager').count(),
            "shg_leads": users.filter(user_type='shg_lead').count(),
        }

    
    def get_member_growth_graph(self, start_date, end_date, cluster_id=None, group_id=None):
        """
        Generate data for member growth graph over time (e.g., monthly).
        """
        filters = {}
        if start_date and end_date:
            filters['created_at__range'] = [start_date, end_date]
        if cluster_id:
            filters['group__cluster'] = cluster_id
        if group_id:
            filters['group'] = group_id

        # Group by month and count new members
        growth_data = (
            Member.objects.filter(**filters)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total_members=Count('id'))
            .order_by('month')
        )

        # Convert to a list of dictionaries for graph consumption
        return [
            {"month": entry['month'].strftime('%Y-%m'), "total_members": entry['total_members']}
            for entry in growth_data
        ]

class LoanSavingReportView(APIView):
    """
    Loan and Saving Report, aggregated for a given cluster or self-help group.
    """

    def get(self, request, entity_type, entity_id):
        """
        Handles reports for either a cluster or a self-help group based on entity_type.
        
        entity_type: 'cluster' or 'group'
        entity_id: ID of the cluster or group
        """
        if entity_type == 'cluster':
            try:
                entity = Cluster.objects.get(id=entity_id)
                groups = SelfHelpGroup.objects.filter(cluster=entity)
                members = Member.objects.filter(group__in=groups)
                entity_name = entity.cluster_name
                total_groups = groups.count()
            except Cluster.DoesNotExist:
                return Response({"error": "Cluster not found"}, status=status.HTTP_404_NOT_FOUND)
        elif entity_type == 'group':
            try:
                entity = SelfHelpGroup.objects.get(id=entity_id)
                members = Member.objects.filter(group=entity)
                entity_name = entity.group_name
                total_groups = None  
            except SelfHelpGroup.DoesNotExist:
                return Response({"error": "SelfHelpGroup not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid entity type. Use 'cluster' or 'group'."}, status=status.HTTP_400_BAD_REQUEST)

        max_loan_round = SixMonthData.objects.filter(member__in=members).aggregate(max_loan=Max('loan_amount_received_shg'))['max_loan']

        iga_capital_range = SixMonthData.objects.filter(member__in=members).aggregate(
            min_iga=Min('iga_capital'), max_iga=Max('iga_capital')
        )

        # Amount of loan received from other sources
        total_loan_other_sources = SixMonthData.objects.filter(member__in=members).aggregate(
            total_loan_other_sources=Sum('loan_amount_from_other_sources')
        )['total_loan_other_sources']

        # Amount of loan taken per category (purpose of loan)
        loan_by_purpose = SixMonthData.objects.filter(member__in=members).values('loan_purpose').annotate(
            total_loan=Sum('loan_amount_received_shg')
        )

        # Range of member’s regular saving
        savings_range = AnnualData.objects.filter(member__in=members).aggregate(
            min_savings=Min('total_savings'), max_savings=Max('total_savings')
        )
        
        # Prepare CSV data
        csv_data = [
            ['Entity', 'Total Members', 'Max Loan Round', 'Min IGA Capital', 'Max IGA Capital', 
             'Total Loan from Other Sources', 'Loan by Purpose', 'Min Savings', 'Max Savings'],
            [
                entity_name,
                members.count(),
                max_loan_round,
                iga_capital_range['min_iga'],
                iga_capital_range['max_iga'],
                total_loan_other_sources,
                ', '.join([f"{item['loan_purpose']}: {item['total_loan']}" for item in loan_by_purpose]),
                savings_range['min_savings'],
                savings_range['max_savings'],
            ],
        ]

        # Create the CSV response
        csv_response = HttpResponse(content_type='text/csv')
        csv_response['Content-Disposition'] = f'attachment; filename="{entity_name}_loan_saving_report.csv"'
        
        writer = csv.writer(csv_response)
        writer.writerows(csv_data)

        return csv_response


class MemberDataReportView(APIView):
    """
    API to fetch member-level report for a group, cluster, or a specific member.
    """

    def get(self, request, *args, **kwargs):
        try:
            # Determine the type of report based on URL parameters
            group_id = kwargs.get("group_id")
            cluster_id = kwargs.get("cluster_id")
            member_id = kwargs.get("member_id")

            if group_id:
                # Fetch members for the given group
                group = get_object_or_404(SelfHelpGroup, id=group_id)
                context = {"group_id": group_id}
                location = group.location
                members = Member.objects.filter(group=group)

            elif cluster_id:
                # Fetch members for the given cluster
                cluster = get_object_or_404(Cluster, id=cluster_id)
                groups = SelfHelpGroup.objects.filter(cluster=cluster)
                members = Member.objects.filter(group__in=groups)
                context = {"cluster_id": cluster_id}
                location =  cluster.location

            elif member_id:
                # Fetch a single member
                member = get_object_or_404(Member, id=member_id)
                members = [member]
                context = {"member_id": member_id} 
                location = member.group.location

            else:
                return Response(
                    {"error": "Invalid request. Provide either group_id, cluster_id, or member_id."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not members:
                return Response({"error": "No members found."}, status=status.HTTP_404_NOT_FOUND)

            # Prepare data
            data = self.get_member_data(members,location = location)

            # Generate CSV response
            return self.generate_csv_response(data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_member_data(self, members, location):
        """
        Helper method to fetch and aggregate member-level data.
        """
        data = []
        for member in members:
            data.append(self.get_single_member_data(member,location))
        return data

    def get_single_member_data(self, member,location):
        """
        Helper method to fetch data for a single member.
        """
        six_month_data = SixMonthData.objects.filter(member=member).order_by('-created_at').first()
        annual_data = AnnualData.objects.filter(member=member).order_by('-created_at').first()
        children_status = AnnualChildrenStatus.objects.filter(member=member).order_by('-created_at').first()

        total_household_size = annual_data.household_size if annual_data else None
        avg_meals_per_day = (
            six_month_data.aggregate(
                avg_meals=Avg(F("meals_per_day_for_children") + F("meals_per_day_for_adults"))
            )["avg_meals"]
            if six_month_data != None
            else None
        )
        total_child_morbidity = (
            six_month_data.aggregate(
                morbidity=Sum(F("days_diarrhea_children") + F("days_other_illness_children"))
            )["morbidity"]
            if six_month_data != None
            else None
        )
        total_child_mortality = annual_data.mortality_children_under_5 if annual_data else None

        school_age_children = 0
        enrolled_children = 0

        if children_status:
            for i in range(1, 6):  # Assuming up to 5 children per member
                school_status = getattr(children_status, f"child_{i}_school_status", None)
                if school_status:
                    school_age_children += 1
                    if school_status == "enrolled":
                        enrolled_children += 1

        percentage_school_enrollment = (
            (enrolled_children / school_age_children) * 100 if school_age_children > 0 else None
        )

        return {
            "member_id": member.id,
            "member_name": member.first_name + " " + member.last_name,
            "location": location,
            "total_household_size": total_household_size,
            "average_meals_per_day": avg_meals_per_day,
            "total_child_morbidity": total_child_morbidity,
            "total_child_mortality": total_child_mortality,
            "percentage_school_enrollment": percentage_school_enrollment,
        }
    
    def generate_csv_response(self, data):
        """
        Generate CSV response from data.
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="member_data_report.csv"'

        writer = csv.writer(response)
        headers = [
            "Member ID",
            "Member Name",
            "Location",
            "Total Household Size",
            "Average Meals Per Day",
            "Total Child Morbidity",
            "Total Child Mortality",
            "Percentage School Enrollment",
        ]
        writer.writerow(headers)

        for row in data:
            writer.writerow([
                row["member_id"],
                row["member_name"],
                row["location"],
                row["total_household_size"],
                row["average_meals_per_day"],
                row["total_child_morbidity"],
                row["total_child_mortality"],
                row["percentage_school_enrollment"],
            ])

        return response



class FacilitatorAnalyticsView(APIView):
    """
    Cluster-level report, aggregated for a given cluster.
    """
    def get(self, request, facilitator_id):
        
        try:
            weema_entity = WEEMAEntities.objects.select_related("user").get(id=facilitator_id)
        except WEEMAEntities.DoesNotExist:
            return Response({"error": "Facilitator not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if weema_entity== None or weema_entity.user.user_type != "facilitator":
            return Response({"error": "User is not a facilitator"}, status=status.HTTP_403_FORBIDDEN)
        
        # Parsing date range parameters
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)


        # Get all groups and members in the cluster
        groups = SelfHelpGroup.objects.filter(facilitator_id=facilitator_id)
        members = Member.objects.filter(group__in=groups)

        # Filtering data based on the time range
        filters = {}
        if start_date and end_date:
            filters['created_at__range'] = [start_date, end_date]

        # Aggregating data
        total_shgs = groups.count()
        total_members = members.count()
        total_household_size = members.aggregate(total=Sum('hh_size'))['total']
        total_savings = AnnualData.objects.filter(member__in=members, **filters).aggregate(total=Sum('total_savings'))['total']
        total_capital = SixMonthData.objects.filter(member__in=members, **filters).aggregate(total=Sum('iga_capital'))['total']
        total_loan_circulated = SixMonthData.objects.filter(member__in=members, **filters).aggregate(total=Sum('loan_amount_received_shg'))['total']
        average_iga_capital = SixMonthData.objects.filter(member__in=members, **filters).aggregate(avg=Avg('iga_capital'))['avg']

        return Response({
            'facilitator': weema_entity.user.first_name + " " + weema_entity.user.last_name, 
            'total_shgs': total_shgs,
            'total_members': total_members,
            'total_household_size': total_household_size,
            'total_savings': total_savings,
            'total_capital': total_capital,
            'total_loan_circulated': total_loan_circulated,
            'average_iga_capital': average_iga_capital,
        }, status=status.HTTP_200_OK)


class LocationLevelAnalyticsPDFView(APIView):
    """
    API View that compiles three location-level analytics reports (household, loan-saving, and group)
    into one PDF file with styled tables. The header row is bold and has a background color.
    Accepts optional query parameters: start_date, end_date, and cluster.
    """

    def get(self, request, *args, **kwargs):
        # Parse optional query parameters
        start_date_str = request.query_params.get('start_date', None)
        end_date_str = request.query_params.get('end_date', None)
        cluster = request.query_params.get('cluster', None)  # This might be an ID or a string
        hh_data = request.query_params.get('hh_data', "Hello")
        shg_data = request.query_params.get('shg_data', None)
        member_data = request.query_params.get('member_data', None)

        # Parse dates if provided
        start_date = parse_datetime(start_date_str) if start_date_str else None
        end_date = parse_datetime(end_date_str) if end_date_str else None

        hh_report = None
        loan_saving_report = None
        group_report = None
        # Get the 2D array reports from the three functions
        if hh_data:
            hh_report = get_location_level_hh_report(start_date=start_date, end_date=end_date, cluster=cluster)
        if member_data:
            loan_saving_report = get_location_level_loan_saving_report(start_date=start_date, end_date=end_date, cluster=cluster)
        if shg_data:
            group_report = get_location_level_group_report(start_date=start_date, end_date=end_date, cluster=cluster)

        # Create a BytesIO buffer for the PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=20, rightMargin=20, topMargin=40, bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()

        # Define an improved table style
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#7ff5b2")),  # Light greenish header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Black text for header
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Default background
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),  # Alternating row colors
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])

        # Helper function to add a section
        def add_section(title, data):
            elements.append(Paragraph(title, styles['Heading2']))
            elements.append(Spacer(1, 12))
            table = Table(data, colWidths=[80, 100, 70, 70, 80, 70, 90])  # Adjusted column widths
            table.setStyle(table_style)
            elements.append(table)
            elements.append(Spacer(1, 24))

        # Add each report as a section
        if  hh_report: add_section("Member Household Report", hh_report)
        if loan_saving_report: add_section("Member Loan & Saving Report", loan_saving_report)
        if group_report: add_section("SHG Data Report", group_report)

        # Build the PDF document
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        return HttpResponse(pdf, content_type='application/pdf')