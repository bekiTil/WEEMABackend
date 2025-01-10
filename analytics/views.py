from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Avg
from data_collection.models import SixMonthData, AnnualData
from cluster_management.models import SelfHelpGroup, Cluster, Member
from user_management.models import CustomUser
from django.utils.dateparse import parse_datetime
from django.contrib.auth.models import AnonymousUser
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
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
        
        # if isinstance(request.user, AnonymousUser):
        #     return JsonResponse({'error': 'Invalid user type'}, status=403)
        user_type = 'super_admin'

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
                "entities": self.get_entity_counts(),
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
