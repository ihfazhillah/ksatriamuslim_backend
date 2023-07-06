from rest_framework import serializers


class SensorLogSerializer(serializers.Serializer):
    token = serializers.CharField()
    sensor = serializers.CharField()
    tracked_time = serializers.DateTimeField()
    message = serializers.CharField()
