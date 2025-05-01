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
from .utils.analytics_util import dump_all_data_report
from cluster_management.models import Cluster
import csv
import zipfile
from io import BytesIO, StringIO


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
        region = request.query_params.get("region", None)
        zone = request.query_params.get("zone", None)
        woreda = request.query_params.get("woreda", None)
        json = request.query_params.get("json", None)

        start_date = parse_datetime(start_date_str) if start_date_str else None
        end_date = parse_datetime(end_date_str) if end_date_str else None

        # Get aggregated analytics per location
        analytics = get_location_level_graph_data(start_date=start_date, end_date=end_date, cluster=cluster, region=region, zone=zone, woreda=woreda)
        
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
            
            # def add_header(canvas, doc):
            #     canvas.saveState()
                
            #     # Logo
            #     logo_path = os.path.join(settings.BASE_DIR, 'logo_real.png')
            #     if os.path.exists(logo_path):
            #         canvas.drawImage(logo_path, 40, 500, width=80, height=80, preserveAspectRatio=True)

            #     # Company Name
            #     canvas.setFont("Helvetica-Bold", 16)
            #     canvas.drawCentredString(400, 560, "WEEMA")

            #     # Report Title
            #     canvas.setFont("Helvetica", 12)
            #     canvas.drawCentredString(400, 540, "Self Help Group (SHG) Data Summary Report")

            #     # Report Date
            #     canvas.setFont("Helvetica", 10)
            #     canvas.drawCentredString(400, 520, f"Date of Report: {datetime.now().strftime('%Y-%m-%d')}")

            #     canvas.restoreState()
            # -------------------
            # Graph 1: Stacked Bar Graph (Groups and Members)
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            x = np.arange(len(locations))
            # Plot total groups (bottom of the bar)
            bar1 = ax1.bar(x, total_groups, label="Total Groups", color="skyblue")
            # Plot total members on top of groups (stacked)
            bar2 = ax1.bar(x, total_members, bottom=total_groups, label="Total Members", color="orange")
            ax1.set_title("Number of Groups & Members by Location")
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
            ax2.set_title("Financial Metrics by Location")
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
            ax3.set_title("Loan Metrics by Location")
            ax3.set_xticks(x)
            ax3.set_xticklabels(locations, rotation=45, ha="right")
            ax3.set_ylabel("Loan Amount")
            ax3.legend()
            fig3.tight_layout()
            pdf.savefig(fig3)
            plt.close(fig3)

            # # Apply header to all pages
            # from reportlab.pdfgen import canvas
            # from reportlab.lib.pagesizes import landscape, letter
            # import os
            # from django.conf import settings
           
            # c = canvas.Canvas(pdf._file, pagesize=landscape(letter))
            # add_header(c, pdf)
            # c.showPage()
            # c.save()

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
        group_age = request.query_params.get('group_age', None)

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
            cluster=cluster_obj ,
            group_age = group_age         
        )
        
        return Response(analytics_result, status=status.HTTP_200_OK)


class DumpAllDataView(APIView):
    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date', None)
        end_date_str = request.query_params.get('end_date', None)
        cluster = request.query_params.get('cluster', None)
        facilitator = request.query_params.get('facilitator', None)
        
        # Extract data using your function (which returns dict of 2D arrays)
        data = dump_all_data_report(start_date=start_date_str, end_date=end_date_str, cluster=cluster, facilitator=facilitator)

        # Create a BytesIO stream to hold the ZIP file
        zip_buffer = BytesIO()

        # Create a ZIP file in memory
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Prepare the 'annual_data' CSV file
            annual_csv_file = StringIO()
            writer = csv.writer(annual_csv_file)
            for row in data["annual_data"]:
                writer.writerow(row)
            # Encode to bytes and write to ZIP
            annual_bytes = annual_csv_file.getvalue().encode('utf-8')
            zip_file.writestr("annual_data.csv", annual_bytes)

            # Prepare the 'six_month_data' CSV file
            six_month_csv_file = StringIO()
            writer = csv.writer(six_month_csv_file)
            for row in data["six_month_data"]:
                writer.writerow(row)
            six_month_bytes = six_month_csv_file.getvalue().encode('utf-8')
            zip_file.writestr("six_month_data.csv", six_month_bytes)

            # Prepare the 'children_status' CSV file
            children_status_csv_file = StringIO()
            writer = csv.writer(children_status_csv_file)
            for row in data["children_status"]:
                writer.writerow(row)
            children_status_bytes = children_status_csv_file.getvalue().encode('utf-8')
            zip_file.writestr("children_status.csv", children_status_bytes)

            # Prepare the 'group_status' CSV file
            group_status_csv_file = StringIO()
            writer = csv.writer(group_status_csv_file)
            for row in data["group_status"]:
                writer.writerow(row)
            group_status_bytes = group_status_csv_file.getvalue().encode('utf-8')
            zip_file.writestr("group_status.csv", group_status_bytes)

        # Ensure the buffer is at the beginning
        zip_buffer.seek(0)

        # Send the ZIP file as the response
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="data.zip"'
        return response