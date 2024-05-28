from django.contrib import admin

from ksatria_muslim.events.models import  Event


class EventAdmin(admin.ModelAdmin):
    list_display = ("date_type", "date", "month", "title")


admin.site.register(Event, EventAdmin)
