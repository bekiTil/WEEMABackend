from rest_framework.viewsets import ModelViewSet
from .models import SixMonthData, AnnualData, AnnualChildrenStatus, AnnualSelfHelpGroupData
from .serializers import SixMonthDataSerializer, AnnualDataSerializer, AnnualChildrenStatusSerializer, AnnualSelfHelpGroupDataSerializer
from .pagination import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class SixMonthDataViewSet(ModelViewSet):
    queryset = SixMonthData.objects.all().order_by('-updated_at')
    serializer_class = SixMonthDataSerializer
    # pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['member', 'active_iga', 'iga_activity_code', 'loan_source_code', 'purpose_of_loan']
    search_fields = ['member__first_name', 'member__last_name', 'iga_activity_code', 'loan_source_code', 'purpose_of_loan']
    ordering_fields = ['created_at', 'updated_at','active_iga', 'iga_activity_code', 'loan_source_code', 'purpose_of_loan', 'approx_monthly_personal_income']

class AnnualDataViewSet(ModelViewSet):
    queryset = AnnualData.objects.all().order_by('-updated_at')
    serializer_class = AnnualDataSerializer
    # pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['member', 'age', 'gender', 'marital_status', 'family_size', 'household_size', 'total_savings', 
                        'loan_rounds_taken', 'estimated_value_of_household_assets', 'household_decision_making', 
                        'community_decision_making', 'mortality_children_under_5', 'mortality_other_household_members', 
                        'housing', 'have_latrine', 'electricity', 'drinking_water']
    search_fields = ['member__first_name', 'member__last_name', 'gender', 'marital_status', 'education_level', 'housing']
    ordering_fields = ['member', 'age', 'gender', 'marital_status', 'family_size','created_at', 'updated_at']

class AnnualChildrenStatusViewSet(ModelViewSet):
    queryset = AnnualChildrenStatus.objects.all().order_by('-updated_at')
    serializer_class = AnnualChildrenStatusSerializer
    # pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['number_of_children','member']
    search_fields = ['member__first_name', 'member__last_name']
    ordering_fields = ['number_of_children', 'created_at', 'updated_at' ]


class AnnualSelfHelpGroupDataViewSet(ModelViewSet):
    queryset = AnnualSelfHelpGroupData.objects.all().order_by('-updated_at')
    serializer_class = AnnualSelfHelpGroupDataSerializer
    # pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['group_iga_code1','group', 'shg_capital', 'largest_loan_given','expenditure_social_savings' ]
    search_fields = ['group_iga_code1','group', 'shg_capital', 'largest_loan_given' ]
    ordering_fields = ['created_at', 'updated_at' ]