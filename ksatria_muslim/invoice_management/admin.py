from django.contrib import admin
from .models import (
    UserClockifyConfig,
    Client,
    Invoice,
    ManualInvoiceEntry,
    ClockifyTimeEntry,
    ClockifyProject,
)


@admin.register(UserClockifyConfig)
class UserClockifyConfigAdmin(admin.ModelAdmin):
    list_display = ["user", "hourly_rate", "conversion_rate", "created_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__username", "company_name"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "Clockify Settings",
            {"fields": ("api_key", "workspace_id", "clockify_user_id")},
        ),
        ("Rate & Currency", {"fields": ("hourly_rate", "conversion_rate")}),
        (
            "Company Information",
            {
                "fields": (
                    "company_name",
                    "company_address_line1",
                    "company_address_line2",
                    "company_address_line3",
                    "company_address_line4",
                )
            },
        ),
        (
            "Payment Information",
            {"fields": ("payment_info_line1", "payment_info_line2")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "email", "phone", "created_at"]
    list_filter = ["created_at", "user"]
    search_fields = ["name", "email", "user__username"]
    readonly_fields = ["created_at", "updated_at"]


class ManualInvoiceEntryInline(admin.TabularInline):
    model = ManualInvoiceEntry
    extra = 0
    fields = ["description", "rate", "quantity", "total_amount"]
    readonly_fields = ["total_amount"]


class ClockifyTimeEntryInline(admin.TabularInline):
    model = ClockifyTimeEntry
    extra = 0
    readonly_fields = [
        "clockify_id",
        "description",
        "start_time",
        "end_time",
        "duration_hours",
        "project_name",
        "task_name",
        "created_at",
    ]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "client",
        "user",
        "invoice_date",
        "total_hours",
        "subtotal_usd",
        "status",
        "created_at",
    ]
    list_filter = ["status", "invoice_date", "created_at", "user"]
    search_fields = ["invoice_number", "client__name", "user__username"]
    readonly_fields = ["subtotal_usd", "total_idr", "created_at", "updated_at"]

    inlines = [ManualInvoiceEntryInline, ClockifyTimeEntryInline]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("user", "client", "invoice_number", "invoice_date", "status")},
        ),
        ("Period", {"fields": ("period_start", "period_end")}),
        ("Clockify Data", {"fields": ("total_hours", "hourly_rate")}),
        (
            "Calculations",
            {
                "fields": ("subtotal_usd", "conversion_rate", "total_idr"),
                "classes": ("collapse",),
            },
        ),
        ("File", {"fields": ("pdf_file",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ManualInvoiceEntry)
class ManualInvoiceEntryAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "invoice",
        "rate",
        "quantity",
        "total_amount",
        "created_at",
    ]
    list_filter = ["created_at", "invoice__user"]
    search_fields = ["description", "invoice__invoice_number"]
    readonly_fields = ["total_amount", "created_at", "updated_at"]


@admin.register(ClockifyTimeEntry)
class ClockifyTimeEntryAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "invoice",
        "start_time",
        "end_time",
        "duration_hours",
        "project_name",
        "created_at",
    ]
    list_filter = ["start_time", "project_name", "invoice__user"]
    search_fields = [
        "description",
        "project_name",
        "task_name",
        "invoice__invoice_number",
    ]
    readonly_fields = ["clockify_id", "project_id", "created_at"]


@admin.register(ClockifyProject)
class ClockifyProjectAdmin(admin.ModelAdmin):
    """Admin for Clockify projects cache"""

    list_display = ["name", "user", "client_name", "archived", "last_synced"]
    list_filter = ["user", "archived", "last_synced", "created_at"]
    search_fields = ["name", "client_name", "clockify_id"]
    readonly_fields = ["clockify_id", "created_at", "updated_at", "last_synced"]

    fieldsets = [
        ("Project Info", {"fields": ("name", "client_name", "color", "archived")}),
        ("Clockify Data", {"fields": ("clockify_id", "user")}),
        ("Cache Management", {"fields": ("last_synced", "created_at", "updated_at")}),
    ]
