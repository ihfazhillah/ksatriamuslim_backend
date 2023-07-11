from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import SensorLogSerializer, BoardLogSerializer
from ..models import Board, Sensor, SensorLog, BoardLog
from ..tasks import send_telegram


@api_view(["POST"])
@permission_classes([AllowAny])
def ping_device(request: Request):
    serializer = BoardLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        board = Board.objects.get(token=serializer.validated_data["token"])
    except Board.DoesNotExist:
        return Response({"error": "board not found"}, status=404)

    BoardLog.objects.create(board=board)
    return Response({"message": "pong"})


@api_view(["POST"])
@permission_classes([AllowAny])
def log_sensor(request: Request):
    serializer = SensorLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        board = Board.objects.get(token=serializer.validated_data["token"])
    except Board.DoesNotExist:
        return Response({"error": "board not found"}, status=404)

    sensor, _ = Sensor.objects.get_or_create(
        board=board,
        label=serializer.validated_data["sensor"],
        type="Pir"
    )

    SensorLog.objects.create(
        sensor=sensor,
        tracked_date=serializer.validated_data["tracked_time"],
        message=serializer.validated_data["message"]
    )

    localtime = timezone.localtime(serializer.validated_data["tracked_time"])
    fmt = "%d/%m/%Y %H:%M:%S WIB"
    send_telegram.delay(
        message=f"Pergerakan terdeteksi di sensor '{sensor.label}'\n\n'{localtime.strftime(fmt)}'"
    )

    return Response({"message": "ok"})
