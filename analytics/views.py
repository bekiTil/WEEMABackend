from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Avg, Max, Min, F, Q
from data_collection.models import SixMonthData, AnnualData, AnnualChildrenStatus
from cluster_management.models import SelfHelpGroup, Cluster, Member
from user_management.models import CustomUser
from django.utils.dateparse import parse_datetime
from django.contrib.auth.models import AnonymousUser
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

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

        return Response({
            'group': group.group_name,
            'total_members': total_members,
            'total_household_size': total_household_size,
            'total_savings': total_savings,
            'total_capital': total_capital,
            'total_loan_circulated': total_loan_circulated,
            'average_iga_capital': average_iga_capital,
        }, status=status.HTTP_200_OK)
        
        
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
                "total_groups": SelfHelpGroup.objects.filter(cluster_id=cluster_id).count(),
                "total_members": Member.objects.filter(group__cluster_id=cluster_id).count(),
                "total_savings": AnnualData.objects.filter(member__group__cluster_id=cluster_id).aggregate(
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
        if cluster_id:
            filters['cluster_id'] = cluster_id  # Assuming users are linked to clusters

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
            filters['group__cluster_id'] = cluster_id
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
            filters['group__cluster_id'] = cluster_id
        if group_id:
            filters['group_id'] = group_id

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
        response_data = {
            'entity': entity_name,
            'total_members': members.count(),
            'max_loan_round': max_loan_round,
            'iga_capital_range': iga_capital_range,
            'total_loan_other_sources': total_loan_other_sources,
            'loan_by_purpose': loan_by_purpose,
            'savings_range': savings_range,
        }

        if total_groups is not None:  
            response_data['total_shgs'] = total_groups

        return Response(response_data, status=status.HTTP_200_OK)


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
                members = Member.objects.filter(group=group)

            elif cluster_id:
                # Fetch members for the given cluster
                cluster = get_object_or_404(Cluster, id=cluster_id)
                groups = SelfHelpGroup.objects.filter(cluster=cluster)
                members = Member.objects.filter(group__in=groups)
                context = {"cluster_id": cluster_id}

            elif member_id:
                # Fetch a single member
                member = get_object_or_404(Member, id=member_id)
                members = [member]
                context = {"member_id": member_id}

            else:
                return Response(
                    {"error": "Invalid request. Provide either group_id, cluster_id, or member_id."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not members:
                return Response({"error": "No members found."}, status=status.HTTP_404_NOT_FOUND)

            # Prepare data
            data = self.get_member_data(members)

            # Add context to the response
            context["data"] = data
            return Response(context, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_member_data(self, members):
        """
        Helper method to fetch and aggregate member-level data.
        """
        data = []
        for member in members:
            data.append(self.get_single_member_data(member))
        return data

    def get_single_member_data(self, member):
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
            if six_month_data.exists()
            else None
        )
        total_child_morbidity = (
            six_month_data.aggregate(
                morbidity=Sum(F("days_diarrhea_children") + F("days_other_illness_children"))
            )["morbidity"]
            if six_month_data.exists()
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
            "member_name": member.name,
            "location": member.cluster.location.name if member.cluster else None,
            "total_household_size": total_household_size,
            "average_meals_per_day": avg_meals_per_day,
            "total_child_morbidity": total_child_morbidity,
            "total_child_mortality": total_child_mortality,
            "percentage_school_enrollment": percentage_school_enrollment,
        }
