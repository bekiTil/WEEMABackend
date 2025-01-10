from django.urls import path
from .views import (
    SystemLevelReportView,
    ClusterLevelReportView,
    SelfHelpGroupLevelReportView,
    DashboardMetricsView
)

urlpatterns = [
    path('reports/system/', SystemLevelReportView.as_view(), name='system-level-report'),
    path('reports/cluster/<uuid:cluster_id>/', ClusterLevelReportView.as_view(), name='cluster-level-report'),
    path('reports/group/<uuid:group_id>/', SelfHelpGroupLevelReportView.as_view(), name='group-level-report'),
    path('reports/dashboard/', DashboardMetricsView.as_view(), name='dashboard-report'),
]
