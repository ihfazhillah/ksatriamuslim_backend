from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

User = get_user_model()


class UserClockifyConfig(models.Model):
    """User-specific Clockify configuration"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="clockify_config"
    )
    api_key = models.CharField(max_length=255, help_text="Clockify API Key")
    workspace_id = models.CharField(max_length=255, help_text="Clockify Workspace ID")
    clockify_user_id = models.CharField(max_length=255, help_text="Clockify User ID")

    # Rate and currency settings
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("25.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Hourly rate in USD",
    )
    conversion_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("16258.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="IDR per USD exchange rate",
    )

    # Company/sender information
    company_name = models.CharField(max_length=255, default="Muhammad Ihfazhillah")
    company_address_line1 = models.CharField(
        max_length=255, default="MASJID MISYKATUL ATSAR KRADENAN TINGKIR LOR TINGKIR"
    )
    company_address_line2 = models.CharField(max_length=255, default="RT 002 RW 006")
    company_address_line3 = models.CharField(
        max_length=255, default="Salatiga Jawa Tengah 50746"
    )
    company_address_line4 = models.CharField(max_length=255, default="Indonesia")

    # Payment information
    payment_info_line1 = models.CharField(
        max_length=255, default="Wise Account: https://wise.com/share/muhammadi404"
    )
    payment_info_line2 = models.CharField(
        max_length=255, default="or search by email: me@ihfazh.com"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Clockify Configuration"
        verbose_name_plural = "User Clockify Configurations"

    def __str__(self):
        return f"{self.user.username} - Clockify Config"


class Client(models.Model):
    """Client information for invoices"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="clients")
    name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    address_line3 = models.CharField(max_length=255, blank=True)
    address_line4 = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "name"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Invoice(models.Model):
    """Invoice model"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="invoices"
    )

    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    # Calculated fields from Clockify
    total_hours = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal_usd = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    conversion_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_idr = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    # File storage
    pdf_file = models.FileField(upload_to="invoices/", blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "invoice_number"]
        ordering = ["-created_at"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client.name}"

    def calculate_totals(self):
        """Calculate totals including manual entries"""
        manual_total = sum(entry.total_amount for entry in self.manual_entries.all())
        self.subtotal_usd = (self.total_hours * self.hourly_rate) + manual_total
        self.total_idr = self.subtotal_usd * self.conversion_rate
        return self.subtotal_usd, self.total_idr


class ManualInvoiceEntry(models.Model):
    """Manual entries for invoices (non-Clockify items)"""

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="manual_entries"
    )
    description = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Manual Invoice Entry"
        verbose_name_plural = "Manual Invoice Entries"

    def save(self, *args, **kwargs):
        self.total_amount = self.rate * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - ${self.total_amount}"


class ClockifyProject(models.Model):
    """Cache for Clockify projects"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="clockify_projects"
    )
    clockify_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    client_name = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=7, blank=True)  # Hex color
    archived = models.BooleanField(default=False)

    # Cache management
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "clockify_id"]
        verbose_name = "Clockify Project"
        verbose_name_plural = "Clockify Projects"

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class ClockifyTimeEntry(models.Model):
    """Store Clockify time entries for invoice tracking"""

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="time_entries"
    )
    clockify_id = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=10, decimal_places=2)

    # Project information
    project_id = models.CharField(max_length=255, blank=True)  # From Clockify API
    project_name = models.CharField(max_length=255, blank=True)  # Resolved from cache
    task_name = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["invoice", "clockify_id"]
        verbose_name = "Clockify Time Entry"
        verbose_name_plural = "Clockify Time Entries"

    def __str__(self):
        return f"{self.description} - {self.duration_hours}h"
