from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Avg
from data_collection.models import SixMonthData, AnnualData
from cluster_management.models import SelfHelpGroup, Cluster, Member
from django.utils.dateparse import parse_datetime

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
