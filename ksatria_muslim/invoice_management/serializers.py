from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    UserClockifyConfig,
    Client,
    Invoice,
    ManualInvoiceEntry,
    ClockifyTimeEntry,
)

User = get_user_model()


class UserClockifyConfigSerializer(serializers.ModelSerializer):
    """Serializer for user Clockify configuration"""

    class Meta:
        model = UserClockifyConfig
        fields = [
            "id",
            "api_key",
            "workspace_id",
            "clockify_user_id",
            "hourly_rate",
            "conversion_rate",
            "company_name",
            "company_address_line1",
            "company_address_line2",
            "company_address_line3",
            "company_address_line4",
            "payment_info_line1",
            "payment_info_line2",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "api_key": {"write_only": True},  # Don't expose API key in responses
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for client model"""

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "address_line1",
            "address_line2",
            "address_line3",
            "address_line4",
            "email",
            "phone",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ManualInvoiceEntrySerializer(serializers.ModelSerializer):
    """Serializer for manual invoice entries"""

    class Meta:
        model = ManualInvoiceEntry
        fields = [
            "id",
            "description",
            "rate",
            "quantity",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "total_amount": {"read_only": True},  # Calculated automatically
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class ClockifyTimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for Clockify time entries"""

    class Meta:
        model = ClockifyTimeEntry
        fields = [
            "id",
            "clockify_id",
            "description",
            "start_time",
            "end_time",
            "duration_hours",
            "project_id",
            "project_name",
            "task_name",
            "created_at",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
        }


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer for invoice list view"""

    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "client_name",
            "invoice_date",
            "total_hours",
            "subtotal_usd",
            "total_idr",
            "status",
            "created_at",
            "updated_at",
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for invoice detail view"""

    client = ClientSerializer(read_only=True)
    manual_entries = ManualInvoiceEntrySerializer(many=True, read_only=True)
    time_entries = ClockifyTimeEntrySerializer(many=True, read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "client",
            "invoice_date",
            "period_start",
            "period_end",
            "total_hours",
            "hourly_rate",
            "subtotal_usd",
            "conversion_rate",
            "total_idr",
            "status",
            "pdf_file",
            "pdf_url",
            "manual_entries",
            "time_entries",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "subtotal_usd": {"read_only": True},
            "total_idr": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None


class CreateInvoiceSerializer(serializers.Serializer):
    """Serializer for creating invoices from Clockify data"""

    client_id = serializers.IntegerField()
    invoice_number = serializers.CharField(max_length=100)
    invoice_date = serializers.DateField()
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
    conversion_rate = serializers.DecimalField(max_digits=10, decimal_places=2)
    excluded_entries = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    manual_entries = serializers.ListField(
        child=serializers.DictField(), required=False, allow_empty=True
    )

    def validate_client_id(self, value):
        user = self.context["request"].user
        try:
            client = Client.objects.get(id=value, user=user)
            return value
        except Client.DoesNotExist:
            raise serializers.ValidationError("Client not found or not owned by user")

    def validate_invoice_number(self, value):
        user = self.context["request"].user
        if Invoice.objects.filter(user=user, invoice_number=value).exists():
            raise serializers.ValidationError("Invoice number already exists")
        return value

    def validate_manual_entries(self, value):
        if not value:
            return value

        for entry in value:
            required_fields = ["description", "rate", "quantity"]
            for field in required_fields:
                if field not in entry:
                    raise serializers.ValidationError(
                        f"Manual entry missing field: {field}"
                    )

            try:
                float(entry["rate"])
                float(entry["quantity"])
            except (ValueError, TypeError):
                raise serializers.ValidationError("Rate and quantity must be numbers")

        return value


class UpdateInvoiceStatusSerializer(serializers.ModelSerializer):
    """Serializer for updating invoice status"""

    class Meta:
        model = Invoice
        fields = ["status"]


class TestClockifyConnectionSerializer(serializers.Serializer):
    """Serializer for testing Clockify connection"""

    api_key = serializers.CharField()
    workspace_id = serializers.CharField()
    clockify_user_id = serializers.CharField()


class TimeEntriesPreviewSerializer(serializers.Serializer):
    """Serializer for previewing time entries before creating invoice"""

    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()

    def validate(self, data):
        if data["period_start"] >= data["period_end"]:
            raise serializers.ValidationError("Start date must be before end date")
        return data
