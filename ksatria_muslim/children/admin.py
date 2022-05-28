from django.contrib import admin

from ksatria_muslim.children.models import Child


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("name", "parent_name")

    @admin.display(description="Parent")
    def parent_name(self, obj):
        return obj.parent.email
