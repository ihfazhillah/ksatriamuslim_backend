from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline

from ksatria_muslim.packages.models import Package, ChildPackage, PackageUsage


@admin.register(Package)
class PackageAdmin(ModelAdmin):
    search_fields = ["title"]
    list_display = ["title", "price", "length"]


class ChildPackageUsageInline(TabularInline):
    model = PackageUsage
    readonly_fields = ["started_at", "finished_at", "duration_seconds"]

    def duration_seconds(self, obj):
        return obj.duration


@admin.register(ChildPackage)
class ChildPackageAdmin(ModelAdmin):
    list_display = ["child", "package", "usage", "is_exhausted"]
    inlines = [ChildPackageUsageInline]

    @admin.display(description="Child")
    def child(self, obj):
        return obj.child.name

    @admin.display(description="Package")
    def package(self, obj):
        return obj.package.title

    @admin.display(description="Usage")
    def usage(self, obj):
        usages = obj.usages.all()
        if not usages:
            return 0
        return sum([usage.duration for usage in usages]) / 60
