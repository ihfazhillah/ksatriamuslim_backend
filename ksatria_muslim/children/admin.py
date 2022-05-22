from django.contrib import admin

from ksatria_muslim.children.models import Child


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("name",)
