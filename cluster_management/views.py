from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Cluster, SelfHelpGroup, Member
from .serializers import ClusterSerializer, SelfHelpGroupSerializer, MemberSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist



# Cluster ViewSet
class ClusterViewSet(ModelViewSet):
    queryset = Cluster.objects.all().order_by('-updated_at')
    serializer_class = ClusterSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'location', 'cluster_manager']
    search_fields = ['cluster_name', 'location']
    ordering_fields = ['cluster_name', 'total_groups', 'created_at', 'updated_at']


# Self Help Group ViewSet
class SelfHelpGroupViewSet(ModelViewSet):
    queryset = SelfHelpGroup.objects.all().order_by('-updated_at')
    serializer_class = SelfHelpGroupSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'location', 'cluster', 'group_leader', 'facilitator', 'longitude', 'latitude', 'location']
    search_fields = ['group_name', 'location', 'facilitator']
    ordering_fields = ['group_name', 'total_members', 'created_at', 'updated_at']


# Member ViewSet
class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all().order_by('-updated_at')
    serializer_class = MemberSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'gender',
        'marital_status',
        'religion',
        'is_other_shg_member_in_house',
        'is_responsible_for_children',
        'group',
        'hh_size',
        'group__cluster',
    ]
    search_fields = ['first_name', 'last_name', 'name', 'hh_size', 'religion']
    ordering_fields = ['hh_size', 'created_at', 'updated_at']


class TransferGroupsAPIView(APIView):
    """
    Transfers all groups that are currently under a specified facilitator or cluster
    to a new target cluster.
    """
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['source_type', 'source_id', 'target_cluster_id'],
            properties={
                'source_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Source type: either 'facilitator' or 'cluster'"
                ),
                'source_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="ID of the source facilitator or cluster"
                ),
                'target_cluster_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="ID of the target cluster to transfer groups to"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Successfully transferred groups",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def post(self, request):
        source_type = request.data.get("source_type")
        source_id = request.data.get("source_id")
        target_cluster_id = request.data.get("target_cluster_id")

        # Validate the source_type
        if source_type not in ["facilitator", "cluster"]:
            return Response(
                {"error": "Invalid source_type. Must be 'facilitator' or 'cluster'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not source_id:
            return Response(
                {"error": "source_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not target_cluster_id:
            return Response(
                {"error": "target_cluster_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate that the target cluster exists
        try:
            target_cluster = Cluster.objects.get(id=target_cluster_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Target cluster not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Query the groups to be transferred based on source_type
        if source_type == "cluster":
            groups_qs = SelfHelpGroup.objects.filter(cluster_id=source_id)
        else:  # source_type == "facilitator"
            groups_qs = SelfHelpGroup.objects.filter(facilitator_id=source_id)

        if groups_qs == None or not groups_qs.exists():
            return Response(
                {"error": "No groups found for the specified source."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Count the groups to be transferred
        groups_count = groups_qs.count()

        # Update the groups: set their cluster to the target cluster and clear the facilitator
        groups_qs.update(cluster=target_cluster, facilitator=None)

        # Optionally, you might need to update any counters on the old or target clusters.
        # For example, you could recalculate total_groups or call your increment/decrement functions.

        return Response(
            {"message": f"Successfully transferred {groups_count} groups to cluster '{target_cluster.cluster_name}'."},
            status=status.HTTP_200_OK
        )


class GetListOfLocaton(APIView):
    def get(self, request):
        locations = (
            SelfHelpGroup.objects.exclude(location__isnull=True)
            .exclude(location="")
            .values_list('location', flat=True)
            .distinct()
        )
        return Response({"distinct_locations": list(locations)})
