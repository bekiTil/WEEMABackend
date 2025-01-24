from django.urls import path
from .views import (
    SystemLevelReportView,
    ClusterLevelReportView,
    SelfHelpGroupLevelReportView,
    DashboardMetricsView,
    LoanSavingReportView,
    MemberDataReportView
)

urlpatterns = [
    path('reports/system/', SystemLevelReportView.as_view(), name='system-level-report'),
    path('reports/cluster/<uuid:cluster_id>/', ClusterLevelReportView.as_view(), name='cluster-level-report'),
    path('reports/group/<uuid:group_id>/', SelfHelpGroupLevelReportView.as_view(), name='group-level-report'),
    path('reports/dashboard/', DashboardMetricsView.as_view(), name='dashboard-report'),
    path('reports/loan-saving/<str:entity_type>/<uuid:entity_id>/', LoanSavingReportView.as_view(), name='loan_saving_report'),
    path('reports/member-data/group/<uuid:group_id>/', MemberDataReportView.as_view(), name="group_member_report"),
    path('reports/member-data/cluster/<uuid:cluster_id>/', MemberDataReportView.as_view(), name="cluster_member_report"),
    path('reports/member-data/member/<uuid:member_id>/', MemberDataReportView.as_view(), name="member_specific_report"),
]
