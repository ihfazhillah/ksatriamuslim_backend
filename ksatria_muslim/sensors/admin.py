from django.contrib import admin
from django.contrib.admin import register
from django.utils import timezone

from .models import Board, BoardLog, Sensor, SensorLog


class BoardLogAdmin(admin.TabularInline):
    model = BoardLog
    readonly_fields = ["created_at"]


@register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["label", "is_active"]

    inlines = [
        BoardLogAdmin,
    ]

    @admin.display(boolean=True)
    def is_active(self, obj):
        latest_log = obj.logs.order_by("-created_at").first()

        if not latest_log:
            return False

        now = timezone.now()
        delta = now - latest_log.created_at
        return delta.seconds <= 30


class SensorLogInline(admin.TabularInline):
    model = SensorLog
    fields = ("message", "tracked_time")


@register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ["label", "type", "board"]
    inlines = [SensorLogInline]
