from django.urls import path
from . import views

app_name = "invoice_management"

urlpatterns = [
    # Dashboard
    path("dashboard/", views.dashboard_stats, name="dashboard-stats"),
    # Clockify Configuration
    path("config/", views.UserClockifyConfigView.as_view(), name="clockify-config"),
    path(
        "config/test/",
        views.TestClockifyConnectionView.as_view(),
        name="test-clockify-connection",
    ),
    path(
        "config/sync-projects/",
        views.SyncClockifyProjectsView.as_view(),
        name="sync-clockify-projects",
    ),
    # Clients
    path("clients/", views.ClientListCreateView.as_view(), name="client-list-create"),
    path("clients/<int:pk>/", views.ClientDetailView.as_view(), name="client-detail"),
    # Invoices
    path(
        "invoices/", views.InvoiceListCreateView.as_view(), name="invoice-list-create"
    ),
    path(
        "invoices/<int:pk>/", views.InvoiceDetailView.as_view(), name="invoice-detail"
    ),
    path(
        "invoices/<int:pk>/status/",
        views.InvoiceStatusUpdateView.as_view(),
        name="invoice-status-update",
    ),
    path(
        "invoices/<int:pk>/pdf/",
        views.DownloadInvoicePDFView.as_view(),
        name="invoice-pdf-download",
    ),
    path(
        "invoices/<int:pk>/regenerate-pdf/",
        views.RegenerateInvoicePDFView.as_view(),
        name="invoice-pdf-regenerate",
    ),
    # Manual Invoice Entries
    path(
        "invoices/<int:invoice_id>/manual-entries/",
        views.ManualInvoiceEntryListCreateView.as_view(),
        name="manual-entry-list-create",
    ),
    path(
        "manual-entries/<int:pk>/",
        views.ManualInvoiceEntryDetailView.as_view(),
        name="manual-entry-detail",
    ),
    # Time Entries Preview
    path(
        "time-entries/preview/",
        views.TimeEntriesPreviewView.as_view(),
        name="time-entries-preview",
    ),
]
