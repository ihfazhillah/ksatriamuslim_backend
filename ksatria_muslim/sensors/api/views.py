from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import SensorLogSerializer
from ..models import Board, Sensor, SensorLog


@api_view(["POST"])
@permission_classes([AllowAny])
def log_sensor(request: Request):
    serializer = SensorLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        board = Board.objects.get(token=serializer.validated_data["token"])
    except Board.DoesNotExist:
        return Response({"error": "board not found"}, status=404)

    sensor = Sensor.objects.get_or_create(
        board=board,
        label=serializer.validated_data["sensor"],
        type="Pir"
    )

    SensorLog.objects.create(
        sensor=sensor,
        tracked_date=serializer.validated_data["tracked_time"],
        message=serializer.validated_data["message"]
    )

    return Response({"message": "ok"})
