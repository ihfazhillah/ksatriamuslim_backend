from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from .models import UserClockifyConfig, Client, Invoice, ManualInvoiceEntry
from .serializers import (
    UserClockifyConfigSerializer,
    ClientSerializer,
    InvoiceListSerializer,
    InvoiceDetailSerializer,
    CreateInvoiceSerializer,
    UpdateInvoiceStatusSerializer,
    TestClockifyConnectionSerializer,
    TimeEntriesPreviewSerializer,
    ManualInvoiceEntrySerializer,
)
from .services import ClockifyService, InvoiceService, InvoiceGeneratorService

User = get_user_model()


class UserClockifyConfigView(APIView):
    """Manage user Clockify configuration"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            config = request.user.clockify_config
            serializer = UserClockifyConfigSerializer(
                config, context={"request": request}
            )
            return Response(serializer.data)
        except UserClockifyConfig.DoesNotExist:
            return Response(
                {"detail": "Configuration not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        try:
            config = request.user.clockify_config
            serializer = UserClockifyConfigSerializer(
                config, data=request.data, context={"request": request}
            )
        except UserClockifyConfig.DoesNotExist:
            serializer = UserClockifyConfigSerializer(
                data=request.data, context={"request": request}
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            config = request.user.clockify_config
            serializer = UserClockifyConfigSerializer(
                config, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserClockifyConfig.DoesNotExist:
            return Response(
                {"detail": "Configuration not found"}, status=status.HTTP_404_NOT_FOUND
            )


class TestClockifyConnectionView(APIView):
    """Test Clockify API connection"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TestClockifyConnectionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Create temporary config for testing
                temp_config = UserClockifyConfig(
                    user=request.user,
                    api_key=serializer.validated_data["api_key"],
                    workspace_id=serializer.validated_data["workspace_id"],
                    clockify_user_id=serializer.validated_data["clockify_user_id"],
                )

                clockify_service = ClockifyService(temp_config)

                # Test connection and sync projects
                result = clockify_service.test_connection_and_sync()

                if result["success"]:
                    return Response(result)
                else:
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response(
                    {"success": False, "error": f"Connection failed: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SyncClockifyProjectsView(APIView):
    """Sync projects from Clockify API"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Check if user has clockify config
            if not hasattr(request.user, "clockify_config"):
                return Response(
                    {"error": "Clockify configuration not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_config = request.user.clockify_config
            clockify_service = ClockifyService(user_config)

            # Sync projects
            project_cache = clockify_service.sync_projects(force_refresh=True)

            return Response(
                {
                    "success": True,
                    "message": f"Successfully synced {len(project_cache)} projects",
                    "projects": [
                        {
                            "id": project.clockify_id,
                            "name": project.name,
                            "client_name": project.client_name,
                            "last_synced": project.last_synced,
                        }
                        for project in project_cache.values()
                    ],
                }
            )

        except UserClockifyConfig.DoesNotExist:
            return Response(
                {"error": "Clockify configuration not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to sync projects: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ClientListCreateView(generics.ListCreateAPIView):
    """List and create clients"""

    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete client"""

    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)


class InvoiceListCreateView(generics.ListCreateAPIView):
    """List invoices and create new invoice from Clockify data"""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateInvoiceSerializer
        return InvoiceListSerializer

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                # Get client
                client = Client.objects.get(
                    id=serializer.validated_data["client_id"], user=request.user
                )

                # Create invoice using service
                invoice = InvoiceService.create_invoice_from_clockify(
                    user=request.user,
                    client=client,
                    invoice_number=serializer.validated_data["invoice_number"],
                    invoice_date=serializer.validated_data["invoice_date"],
                    period_start=serializer.validated_data["period_start"],
                    period_end=serializer.validated_data["period_end"],
                    tax_rate=serializer.validated_data.get("tax_rate", 0),
                    conversion_rate=serializer.validated_data.get("conversion_rate"),
                    excluded_entries=serializer.validated_data.get(
                        "excluded_entries", []
                    ),
                    manual_entries=serializer.validated_data.get("manual_entries", []),
                )

                # Return invoice detail
                response_serializer = InvoiceDetailSerializer(
                    invoice, context={"request": request}
                )
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete invoice"""

    serializer_class = InvoiceDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)


class InvoiceStatusUpdateView(APIView):
    """Update invoice status"""

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
        serializer = UpdateInvoiceStatusSerializer(
            invoice, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeEntriesPreviewView(APIView):
    """Preview time entries for a period before creating invoice"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TimeEntriesPreviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if user has clockify config
            if not hasattr(request.user, "clockify_config"):
                return Response(
                    {"error": "Clockify configuration not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_config = request.user.clockify_config
            clockify_service = ClockifyService(user_config)

            # Get time entries from Clockify
            time_entries = clockify_service.get_time_entries(
                start_date=serializer.validated_data["period_start"],
                end_date=serializer.validated_data["period_end"],
            )

            # If no entries found, return empty response
            if not time_entries:
                return Response(
                    {
                        "entries": [],
                        "total_hours": 0.0,
                        "total_amount": 0.0,
                        "summary": {},
                    }
                )

            total_hours = clockify_service.calculate_duration(time_entries)
            total_cost_usd = float(total_hours) * float(user_config.hourly_rate)
            total_cost_idr = total_cost_usd * float(user_config.conversion_rate)

            # Get project cache ONCE for all entries - PERFORMANCE OPTIMIZATION
            project_cache = clockify_service.get_projects()

            # Calculate project summary
            project_summary = {}

            # Format entries for response
            formatted_entries = []
            for entry in time_entries:
                try:
                    time_interval = entry.get("timeInterval", {})
                    duration_str = time_interval.get("duration", "PT0S")
                    duration_hours = (
                        clockify_service.parse_duration(duration_str) / 3600
                    )

                    # Calculate amount for this entry
                    entry_amount = (
                        float(duration_hours)
                        * float(user_config.hourly_rate)
                        * float(user_config.conversion_rate)
                    )

                    # Get project name from cache (already loaded once)
                    project_id = entry.get("projectId", "")
                    if project_id and project_id in project_cache:
                        project_name = project_cache[project_id].name
                    else:
                        project_name = "Unknown Project"
                    if project_name not in project_summary:
                        project_summary[project_name] = {"hours": 0.0, "amount": 0.0}
                    project_summary[project_name]["hours"] += float(duration_hours)
                    project_summary[project_name]["amount"] += float(entry_amount)

                    formatted_entries.append(
                        {
                            "id": entry.get("id"),
                            "clockify_id": entry.get("id"),
                            "description": entry.get("description", ""),
                            "project_name": project_name,
                            "duration": f"{duration_hours:.2f}h",
                            "start_time": clockify_service.convert_to_wib(
                                time_interval.get("start", "")
                            ),
                            "end_time": clockify_service.convert_to_wib(
                                time_interval.get("end", "")
                            ),
                            "billable": True,  # Assume all entries are billable
                            "hourly_rate": float(user_config.hourly_rate),
                            "total_amount": float(entry_amount),
                            "created_at": time_interval.get("start", ""),
                        }
                    )
                except Exception as entry_error:
                    print(
                        f"Error processing entry {entry.get('id', 'unknown')}: {entry_error}"
                    )
                    continue

            return Response(
                {
                    "entries": formatted_entries,
                    "total_hours": float(total_hours),
                    "total_amount": float(total_cost_idr),
                    "summary": project_summary,
                }
            )

        except UserClockifyConfig.DoesNotExist:
            return Response(
                {"error": "Clockify configuration not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(f"TimeEntries preview error: {e}")
            return Response(
                {"error": f"Failed to fetch time entries: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DownloadInvoicePDFView(APIView):
    """Download invoice PDF"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk, user=request.user)

        if not invoice.pdf_file:
            # Generate PDF if not exists
            try:
                user_config = request.user.clockify_config
                pdf_service = InvoiceGeneratorService(user_config)
                pdf_service.save_invoice_pdf(invoice)
            except UserClockifyConfig.DoesNotExist:
                return Response(
                    {"error": "Clockify configuration not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"error": f"Error generating PDF: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Return PDF file
        response = HttpResponse(invoice.pdf_file.read(), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        )
        return response


class RegenerateInvoicePDFView(APIView):
    """Regenerate invoice PDF"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk, user=request.user)

        try:
            user_config = request.user.clockify_config
            pdf_service = InvoiceGeneratorService(user_config)
            filename = pdf_service.save_invoice_pdf(invoice)

            return Response(
                {
                    "success": True,
                    "message": f"PDF regenerated: {filename}",
                    "pdf_url": request.build_absolute_uri(invoice.pdf_file.url)
                    if invoice.pdf_file
                    else None,
                }
            )

        except UserClockifyConfig.DoesNotExist:
            return Response(
                {"error": "Clockify configuration not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Error regenerating PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ManualInvoiceEntryListCreateView(generics.ListCreateAPIView):
    """List and create manual entries for an invoice"""

    serializer_class = ManualInvoiceEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        invoice_id = self.kwargs["invoice_id"]
        return ManualInvoiceEntry.objects.filter(
            invoice_id=invoice_id, invoice__user=self.request.user
        )

    def perform_create(self, serializer):
        invoice_id = self.kwargs["invoice_id"]
        invoice = get_object_or_404(Invoice, id=invoice_id, user=self.request.user)
        serializer.save(invoice=invoice)

        # Recalculate invoice totals
        invoice.calculate_totals()
        invoice.save()


class ManualInvoiceEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete manual invoice entry"""

    serializer_class = ManualInvoiceEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ManualInvoiceEntry.objects.filter(invoice__user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        # Recalculate invoice totals
        invoice = serializer.instance.invoice
        invoice.calculate_totals()
        invoice.save()

    def perform_destroy(self, instance):
        invoice = instance.invoice
        instance.delete()
        # Recalculate invoice totals
        invoice.calculate_totals()
        invoice.save()


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    user = request.user

    # Get invoice stats
    invoices = Invoice.objects.filter(user=user)
    total_invoices = invoices.count()
    draft_invoices = invoices.filter(status="draft").count()
    sent_invoices = invoices.filter(status="sent").count()
    paid_invoices = invoices.filter(status="paid").count()

    # Calculate total earnings
    total_earnings_usd = sum(
        invoice.subtotal_usd for invoice in invoices.filter(status__in=["sent", "paid"])
    )
    total_earnings_idr = sum(
        invoice.total_idr for invoice in invoices.filter(status__in=["sent", "paid"])
    )

    # Get recent invoices
    recent_invoices = invoices.order_by("-created_at")[:5]
    recent_invoices_data = InvoiceListSerializer(recent_invoices, many=True).data

    return Response(
        {
            "stats": {
                "total_invoices": total_invoices,
                "draft_invoices": draft_invoices,
                "sent_invoices": sent_invoices,
                "paid_invoices": paid_invoices,
                "total_earnings_usd": float(total_earnings_usd),
                "total_earnings_idr": float(total_earnings_idr),
            },
            "recent_invoices": recent_invoices_data,
            "has_clockify_config": hasattr(user, "clockify_config"),
        }
    )
