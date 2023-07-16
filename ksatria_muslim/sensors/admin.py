from django.contrib import admin
from django.contrib.admin import register
from django.utils import timezone

from .models import Board, BoardLog, Sensor, SensorLog, ImouAccount, CCTVCamera


class BoardLogAdmin(admin.TabularInline):
    extra = 0
    model = BoardLog
    readonly_fields = ["created"]
    max_num = 10
    ordering = ["-created"]


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
    max_num = 10
    ordering = ["-tracked_date"]



@register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ["label", "type", "board"]
    inlines = [SensorLogInline]

class CameraAdminInline(admin.TabularInline):
    model = CCTVCamera
    extra = 0

@register(ImouAccount)
class ImouAccountAdmin(admin.ModelAdmin):
    list_display = ["label"]
    inlines = [CameraAdminInline]
