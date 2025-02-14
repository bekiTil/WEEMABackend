from django.urls import path
from .views import (
    SystemLevelReportView,
    ClusterLevelReportView,
    SelfHelpGroupLevelReportView,
    DashboardMetricsView,
    LoanSavingReportView,
    MemberDataReportView,
    FacilitatorAnalyticsView,
    LocationLevelAnalyticsPDFView
)
from .graph_views import LocationAnalyticsGraphsPDFView, GroupLevelFinancialMetricsAPIView, DumpAllDataView

urlpatterns = [
    path('reports/system/', SystemLevelReportView.as_view(), name='system-level-report'),
    path('reports/cluster/<uuid:cluster_id>/', ClusterLevelReportView.as_view(), name='cluster-level-report'),
    path('reports/facilitator/<uuid:facilitator_id>/', FacilitatorAnalyticsView.as_view(), name='cluster-level-report'),
    path('reports/group/<uuid:group_id>/', SelfHelpGroupLevelReportView.as_view(), name='group-level-report'),
    path('reports/dashboard/', DashboardMetricsView.as_view(), name='dashboard-report'),
    path('reports/loan-saving/<str:entity_type>/<uuid:entity_id>/', LoanSavingReportView.as_view(), name='loan_saving_report'),
    path('reports/member-data/group/<uuid:group_id>/', MemberDataReportView.as_view(), name="group_member_report"),
    path('reports/member-data/cluster/<uuid:cluster_id>/', MemberDataReportView.as_view(), name="cluster_member_report"),
    path('reports/member-data/member/<uuid:member_id>/', MemberDataReportView.as_view(), name="member_specific_report"),
    path('reports/pdf/table/', LocationLevelAnalyticsPDFView.as_view(), name="pdf_table_report"),
    path('reports/pdf/graph/highlevel', LocationAnalyticsGraphsPDFView.as_view(), name="pdf_graph_heigh_level_report"),
    path('reports/pdf/graph/quality-control', GroupLevelFinancialMetricsAPIView.as_view(), name="pdf_graph_quality_control_report"),
    path('reports/dump-all-data', DumpAllDataView.as_view(), name="dump_all_data"),
]
