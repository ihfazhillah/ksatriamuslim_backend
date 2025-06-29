from django.urls import path
from .views import BoardStateView, TaskUpdateView

app_name = "kidskanbantask"

urlpatterns = [
    path("board/", BoardStateView.as_view(), name="board_state"),
    path("tasks/<str:taskId>/", TaskUpdateView.as_view(), name="task_update"),
]
