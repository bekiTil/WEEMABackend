import io
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.graph_analytics import get_location_level_graph_data, get_group_level_financial_metrics
from cluster_management.models import Cluster


class LocationAnalyticsGraphsPDFView(APIView):
    """
    API view to generate a PDF file containing three graphs based on location-level analytics:
      1. Stacked bar graph: x-axis is location; bottom stack = total groups, top stack = total members.
      2. Grouped bar chart: three bars per location representing total savings, total capital, and total loan circulated.
      3. Line chart: two lines for each location representing max loan taken and total loan from other sources.
    Accepts optional query parameters: start_date, end_date, cluster.
    """

    def get(self, request):
        # Parse optional query parameters
        start_date_str = request.query_params.get("start_date", None)
        end_date_str = request.query_params.get("end_date", None)
        cluster = request.query_params.get("cluster", None)
        json = request.query_params.get("json", None)

        start_date = parse_datetime(start_date_str) if start_date_str else None
        end_date = parse_datetime(end_date_str) if end_date_str else None

        # Get aggregated analytics per location
        analytics = get_location_level_graph_data(start_date=start_date, end_date=end_date, cluster=cluster)
        
        if json:
            return Response(analytics, status = status.HTTP_200_OK)

        # Sort locations for consistent ordering
        locations = sorted(analytics.keys())

        # Prepare arrays for plotting
        total_groups = [analytics[loc]["total_groups"] for loc in locations]
        total_members = [analytics[loc]["total_members"] for loc in locations]
        total_savings = [analytics[loc]["total_savings"] for loc in locations]
        total_capital = [analytics[loc]["total_capital"] for loc in locations]
        total_loan_circulated = [analytics[loc]["total_loan_circulated"] for loc in locations]
        max_loan_taken = [analytics[loc]["max_loan_taken"] for loc in locations]
        total_loan_other_sources = [analytics[loc]["total_loan_other_sources"] for loc in locations]

        # Create a BytesIO buffer to save the PDF
        buffer = io.BytesIO()

        # Create a PdfPages object to compile multiple pages into a single PDF
        with PdfPages(buffer) as pdf:
            # -------------------
            # Graph 1: Stacked Bar Graph (Groups and Members)
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            x = np.arange(len(locations))
            # Plot total groups (bottom of the bar)
            bar1 = ax1.bar(x, total_groups, label="Total Groups", color="skyblue")
            # Plot total members on top of groups (stacked)
            bar2 = ax1.bar(x, total_members, bottom=total_groups, label="Total Members", color="orange")
            ax1.set_title("Stacked Bar Graph: Groups & Members by Location")
            ax1.set_xticks(x)
            ax1.set_xticklabels(locations, rotation=45, ha="right")
            ax1.set_ylabel("Count")
            ax1.legend()
            fig1.tight_layout()
            pdf.savefig(fig1)
            plt.close(fig1)

            # -------------------
            # Graph 2: Grouped Bar Chart for Financial Metrics
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            x = np.arange(len(locations))
            width = 0.25  # width of the bars
            ax2.bar(x - width, total_savings, width, label="Total Savings", color="green")
            ax2.bar(x, total_capital, width, label="Total Capital", color="blue")
            ax2.bar(x + width, total_loan_circulated, width, label="Total Loan Circulated", color="red")
            ax2.set_title("Grouped Bar Chart: Financial Metrics by Location")
            ax2.set_xticks(x)
            ax2.set_xticklabels(locations, rotation=45, ha="right")
            ax2.set_ylabel("Amount")
            ax2.legend()
            fig2.tight_layout()
            pdf.savefig(fig2)
            plt.close(fig2)

            # -------------------
            # Graph 3: Line Chart for Loan Data
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            x = np.arange(len(locations))
            ax3.plot(x, max_loan_taken, marker="o", linestyle="-", label="Max Loan Taken", color="purple")
            ax3.plot(x, total_loan_other_sources, marker="o", linestyle="-", label="Total Loan from Other Sources", color="brown")
            ax3.set_title("Line Chart: Loan Metrics by Location")
            ax3.set_xticks(x)
            ax3.set_xticklabels(locations, rotation=45, ha="right")
            ax3.set_ylabel("Loan Amount")
            ax3.legend()
            fig3.tight_layout()
            pdf.savefig(fig3)
            plt.close(fig3)

        # Get PDF data from buffer
        pdf_data = buffer.getvalue()
        buffer.close()

        # Return PDF as response
        return HttpResponse(pdf_data, content_type="application/pdf")
  

class GroupLevelFinancialMetricsAPIView(APIView):
    
    def get(self, request):
        # Get optional date range from query parameters
        start_date_str = request.query_params.get('start_date', None)
        end_date_str = request.query_params.get('end_date', None)
        start_date = parse_datetime(start_date_str) if start_date_str else None
        end_date = parse_datetime(end_date_str) if end_date_str else None

        # Get the cluster parameter (if provided) and convert to a Cluster instance
        cluster_id = request.query_params.get('cluster', None)
        cluster_obj = None
        if cluster_id:
            try:
                cluster_obj = Cluster.objects.get(id=cluster_id)
            except Cluster.DoesNotExist:
                return Response({"error": "Cluster not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Call the aggregation function with the provided filters
        analytics_result = get_group_level_financial_metrics(
            start_date=start_date_str,   
            end_date=end_date_str,
            cluster=cluster_obj          
        )
        
        return Response(analytics_result, status=status.HTTP_200_OK)
