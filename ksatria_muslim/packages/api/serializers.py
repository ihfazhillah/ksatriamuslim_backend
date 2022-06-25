from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ksatria_muslim.children.models import Child
from ksatria_muslim.packages.models import Package, PackageUsage


class PackageSerializer(serializers.RelatedField):
    default_error_messages = {
        'required': 'This field is required.',
        'does_not_exist': 'Invalid title "{pk_value}" - object does not exist.',
        'incorrect_type': 'Incorrect type. Expected pk value, received {data_type}.',
    }
    def to_representation(self, value):
        return value.title

    def to_internal_value(self, data):
        qs = self.get_queryset()
        try:
            return qs.get(title=data)
        except ObjectDoesNotExist:
            self.fail("does_not_exists", pk_value=data)


class PackageLogUsageSerializer(serializers.Serializer):
    child = serializers.PrimaryKeyRelatedField(queryset=Child.objects.all())
    package = PackageSerializer(queryset=Package.objects.all())
    finished_at = serializers.DateTimeField(required=False, format="%Y%m%d%H%M%S", input_formats=["%Y%m%d%H%M%S"])
    started_at = serializers.DateTimeField(required=False, format="%Y%m%d%H%M%S", input_formats=["%Y%m%d%H%M%S"])


class BuyPackageBodySerializer(serializers.Serializer):
    child = serializers.PrimaryKeyRelatedField(queryset=Child.objects.all())
    package = PackageSerializer(queryset=Package.objects.all())
