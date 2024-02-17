from django.urls import path

from ksatria_muslim.children_task import views

app_name = "children_task"

urlpatterns = [
    path("children/", views.get_children, name="get-children"),
    path("children/<child_id>/tasks/", views.get_task_list, name="get-task-list"),
    path("mark-as-finished/", views.mark_as_finished, name="mark-as-finished"),
    path("confirm/", views.confirm, name="confirm"),
]
