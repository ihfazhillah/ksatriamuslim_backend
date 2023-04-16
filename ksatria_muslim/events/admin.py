from django.contrib import admin
from django.http import HttpRequest

from ksatria_muslim.events.models import EventOrganizer, Event, EventPresenter

admin.site.register(EventOrganizer, admin.ModelAdmin)
admin.site.register(EventPresenter, admin.ModelAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "presenter", "organizer", "started_at")
    fields = ("title", "thumbnail", "organizer", "presenter", "started_at", "youtube_link", "zoom_link")
    ordering = ["-started_at"]

    def save_model(self, request: HttpRequest, obj, form, change) -> None:
        obj.submitter = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Event, EventAdmin)
