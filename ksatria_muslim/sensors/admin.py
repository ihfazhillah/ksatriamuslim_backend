from django.contrib import admin
from django.contrib.admin import register
from django.utils import timezone

from .models import Board, BoardLog, Sensor, SensorLog


class BoardLogAdmin(admin.TabularInline):
    extra = 0
    model = BoardLog
    readonly_fields = ["created"]

    def get_queryset(self, request):
        qs = super().get_queryset(request).order_by("-created")
        return qs[:10]


@register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["label", "is_active"]

    inlines = [
        BoardLogAdmin,
    ]

    @admin.display(boolean=True)
    def is_active(self, obj):
        latest_log = obj.logs.order_by("-created").first()

        if not latest_log:
            return False

        now = timezone.now()
        delta = now - latest_log.created
        return delta.seconds <= 30


class SensorLogInline(admin.TabularInline):
    model = SensorLog
    fields = ("message", "tracked_date")

    def get_queryset(self, request):
        qs = super().get_queryset(request).order_by("-tracked_date")
        return qs[:10]


@register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ["label", "type", "board"]
    inlines = [SensorLogInline]
