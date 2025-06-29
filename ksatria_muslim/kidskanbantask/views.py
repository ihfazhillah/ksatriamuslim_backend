from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .db import get_board_state_data, update_task_status
from .serializers import BoardStateSerializer, TaskSerializer

class BoardStateView(APIView):
    """Handles GET requests to fetch the entire board state."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = get_board_state_data()
        serializer = BoardStateSerializer(data)
        return Response(serializer.data)

class TaskUpdateView(APIView):
    """Handles PATCH requests to update a task's completion status."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, taskId, *args, **kwargs):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            completed = serializer.validated_data['completed']
            updated_task = update_task_status(taskId, completed)

            if updated_task:
                return Response(TaskSerializer(updated_task).data)
            else:
                return Response({'code': 'not_found', 'message': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
