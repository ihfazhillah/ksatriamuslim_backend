from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ksatria_muslim.packages.api.serializers import PackageLogUsageSerializer
from ksatria_muslim.packages.models import PackageUsage, ChildPackage


class PackageUsageViewSet(GenericViewSet):
    queryset = PackageUsage.objects.all()

    @action(methods=["POST"], detail=False)
    def log(self, request, pk=None):
        serializer = PackageLogUsageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        child = serializer.validated_data["child"]
        package = serializer.validated_data["package"]
        started_at = serializer.validated_data.get("started_at")
        finished_at = serializer.validated_data.get("finished_at")

        child_package = ChildPackage.objects.filter(
            child=child,
            package=package,
            is_exhausted=False
        ).first()

        if started_at:
            # create
            PackageUsage.objects.create(
                child_package=child_package,
                started_at=started_at
            )

        elif finished_at:
            log = PackageUsage.objects.filter(
                child_package=child_package,
                started_at__isnull=False,
                finished_at__isnull=True
            ).first()
            if log:
                log.finished_at = finished_at
                log.save()

            child_package.refresh_from_db()
            if child_package.remaining <= 0.0:
                child_package.is_exhausted = True
                child_package.save()

        return Response({"ok": True})
